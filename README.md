# Social Info
Get info about the followers of another account. Works with Twitter, Instagram and TikTok.

## Requirements
- python3, pip
- RapidAPI token (for TikTok)
- Twitter Bearer Token
- Instagram username and password

## Usage
Install dependencies:
```bash
$ pip3 install -r requirements.txt
```

```bash
Usage:
    social_info.py instagram followers <user_id> [--inspect | --load-cursor] [<output>]
    social_info.py twitter followers <user_id> [--inspect | --load-cursor] [<output>]
    social_info.py tiktok followers <user_id> [--inspect | --load-cursor] [<output>]
    social_info.py (-h | --help)

Options:
    --load-cursor       Load cursors from save data (recommended if you're picking up a previous session)
    -i --inspect        Show the available dictionary keys within a response (won't save output)
    -h --help           Show this message
```
