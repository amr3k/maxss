# Description

This script fetches a url list from archive.org and applies a filter to get rid of static files.

## Requirements

- Linux shell (bash/zsh)
- Python3
- requests

## Installation

- `git clone https://github.com/ShogunExecutioner/web-archive-cached-urls.git && cd web-archive-cached-urls`
- Install a virtual environment (Optional) `python -m venv .env`
- Install requests module
- Check `static_file_extensions.json` file if you want to add/remove extensions for the filter.

## Usage

`python cached_urls.py target_domain`
