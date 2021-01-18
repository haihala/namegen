# Namegen

Name generator that take in a word or a list of words and produces a list of names.

## Setup

1. Install python3
2. `python -m pip install -r requirements.txt`

## Usage

`python names.py <lang> <words>`. Lang is an abreviation of a language, like 'fr' for French or 'de' for German. Words is one or more words to do the deed to.

The script uses a 'libraries' of translations so it saves a bit on translator limits. These are saved by language to a folder called `libraries` next to the script. It will create the folder automatically but will ask before doing so. 