import os
import requests
import yt_dlp
import json
import sys

api_key = os.environ.get("OPENAI_API_KEY")

def download_audio(youtube_link, file_path):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{file_path}.%(ext)s",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "worse"},
            {"key": "FFmpegMetadata"},
        ],
        'postprocessor_args': [
            '-ar', '16000',  # sample rate
            '-ac', '1'  # mono
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_link])

    return f"{file_path}.mp3"

def transcribe_audio(file_path):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}

    with open(file_path, "rb") as audio_file:
        files = {"file": (os.path.basename(file_path), audio_file)}
        data = {"model": "whisper-1", "language": "en"}
        response = requests.post(url, headers=headers, files=files, data=data)

    print("Transcription:", response.json())

    return response.json()["text"]

def summarize_text(transcription, model, max_tokens, prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": model,
        "temperature": 0,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": transcription,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    summary = response.json()['choices'][0]['message']['content']
    return summary.strip()

def process_video(youtube_link):
    file_path = "temp_audio"
    output_file_path = download_audio(youtube_link, file_path)
    transcription = transcribe_audio(output_file_path)

    # Extract video title
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_link, download=False)
        video_title = info_dict["title"]

    # Save the transcription to a file
    folder_name = "transcriptions"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    video_id = youtube_link.split("watch?v=")[-1]
    file_prefix = f"{folder_name}/{video_id}"

    with open(f"{file_prefix}_transcription.txt", "w") as f:
        f.write(f"Title: {video_title}\n\n{transcription}")

    summary = summarize_text(transcription, video_model, video_max_tokens, video_prompt)

    # Save the summary to a file
    with open(f"{file_prefix}_summary.txt", "w") as f:
        f.write(f"Title: {video_title}\n\n{summary}")

    print(f"\nSummary for {youtube_link}:\n", summary)

    # Optional: Remove the downloaded audio file after transcription
    os.remove(output_file_path)

    return f"Title: {video_title}\n\n{summary}"

def main(video_links):
    video_summaries = []
    for link in video_links:
        video_summary = process_video(link)
        video_summaries.append(video_summary)
    video_summaries_combined ="\n\n".join(video_summaries).strip()
    summary = summarize_text(video_summaries_combined, summary_model, summary_max_tokens, summary_prompt)
    with open("result.md", "w") as f:
        f.write(summary)


video_max_tokens = 400
video_prompt = "Create a list of the most important points from the above video transcription."
video_model = "gpt-3.5-turbo"

summary_max_tokens = 2048
summary_prompt = "Create a insightful markdown document containing everything mentioned in the above list of important points taken from videos transcriptions."
summary_model = "gpt-4"

max_videos = ((8192 - summary_max_tokens) // video_max_tokens)

if __name__ == "__main__":
    print("Max videos:", max_videos)
    video_links = [
        "https://www.youtube.com/watch?v=k9HYC0EJU6E", # What is DEFI? Decentralized Finance Explained (Ethereum, MakerDAO, Compound, Uniswap, Kyber)
        "https://www.youtube.com/watch?v=JCYIFtb8DwM", # TOP 3 DEFI WALLETS FOR 2021 - What Features Do They Support?
        "https://www.youtube.com/watch?v=pWGLtjG-F5c", # CODE IS LAW? Smart Contracts Explained (Ethereum, DeFi)
        "https://www.youtube.com/watch?v=LpjMgS4OVzs", # A Short Story of UNISWAP and UNI Token. DEFI Explained
        "https://www.youtube.com/watch?v=aTp9er6S73M", # Lending And Borrowing In DEFI Explained - Aave, Compound
        "https://www.youtube.com/watch?v=cizLhxSKrAc", # How do LIQUIDITY POOLS work? (Uniswap, Curve, Balancer) | DEFI Explained
        "https://www.youtube.com/watch?v=8XJ1MSTEuU0", # What Is IMPERMANENT LOSS? DEFI Explained - Uniswap, Curve, Balancer, Bancor
        "https://www.youtube.com/watch?v=ClnnLI1SClA", # What Is YIELD FARMING? DEFI Explained (Compound, Balancer, Curve, Synthetix, Ren)
        "https://www.youtube.com/watch?v=qG1goOptZ5w", # YEARN FINANCE And YFI Token Explained | DeFi, Ethereum
        "https://www.youtube.com/watch?v=9vTaNl2_B8A", # What are YEARN VAULTS? ETH Vault Explained | DEFI, YIELD FARMING
        "https://www.youtube.com/watch?v=mCJUhnXQ76s", # Borrow Millions In DEFI With NO COLLATERAL? FLASH LOANS Explained (Aave, dYdX)
        "https://www.youtube.com/watch?v=UFjXwrCGuog", # What Is a VAMPIRE ATTACK? SUSHISWAP Saga Explained
        "https://www.youtube.com/watch?v=e-8yjmsshFg", # How Does AMPLEFORTH Work? DEFI Explained
        "https://www.youtube.com/watch?v=Xdkkux6OxfM", # What Are NFTs and How Can They Be Used in Decentralized Finance? DEFI Explained
        "https://www.youtube.com/watch?v=BgCgauWVTs0", # Ethereum LAYER 2 SCALING Explained (Rollups, Plasma, Channels, Sidechains)
    ]
    if len(video_links) > max_videos:
        print(f"Maximum number of videos allowed with current configuration is {max_videos}")
        sys.exit(1)
    main(video_links)
