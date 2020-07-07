# Description

This script fetches a url list from archive.org and applies a filter to get rid of static files.

## Requirements

- Linux shell (bash/zsh)
- Python 3.7+
- [XSShunter account](https://xsshunter.com) (or your custom blind xss payload)

## Installation

- `git clone https://github.com/ShogunExecutioner/noob-xss.git && cd noob-xss`
- Install a virtual environment (Optional) `python -m venv .env`
- `pip install -r requirements.txt`
- Check `static/extensions.json` file if you want to add/remove extensions for the filter.
- Edit `static/config.json` add your own blind xss payload

## Usage

`python cached_urls.py target_domain`

## TODO list

- WAF detector
- Proxy
- Multiple payloads support
- Command line arguments
- Option to use a file directly instead of archive.org
- Code optimization
- Advanced Logging
- Rewriting this README
- Documentation

## Special thanks

-
-
-
-
