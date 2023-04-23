# Youtube Video Reducer

[![](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

Takes a list of youtube video links:

![image](https://user-images.githubusercontent.com/7863230/233854751-689e352e-1070-4004-af1a-2afa53df8509.png)

Reduces into whatever you configured:

- [example individual video transcriptions and summaries](https://github.com/MarcoWorms/youtube-videos-reducer/tree/main/example_transcriptions)
- [example final summary made from all video summaries](https://github.com/MarcoWorms/youtube-videos-reducer/blob/main/example_result.md)

## Develop

- `git clone https://github.com/MarcoWorms/youtube-videos-reducer.git`
- `cd youtube-videos-reducer`
- `pip install -r "requirements.txt"`
- export OPENAI_API_KEY to your environment variables
- `python main.py`
