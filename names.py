from googletrans import Translator  # One day this should be the official api
from PyDictionary import PyDictionary
from pprint import pprint
import argparse
from statistics import median
from random import randint, normalvariate, choice, random
from os.path import join as path_join
from os.path import isdir, isfile
from os import mkdir, getcwd
import io

CHUNK_MIN = 2
CHUNK_MAX = 4
BATCH_SIZE = 50
CHUNKS_MEAN = 2.5
CHUNKS_STD = 2
CHUNKS_MIN = 2
CHUNKS_MAX = 8
TL_OUTLIER = 5
LIBRARY_FOLDER = "libraries"
SPACE_ACCUMULATOR_BASE = -0.5
SPACE_ACCUMULATOR_INCREMENT = 0.2

def get_chunk(text):
    cl = randint(CHUNK_MIN, min(CHUNK_MAX, len(text)))
    return text[:cl], text[cl:]

def add_space(text):
    accumulator = SPACE_ACCUMULATOR_BASE
    index = 0
    while index < len(text)-1:
        if random() < accumulator:
            text = text[:index] + ' ' + text[index:]
            accumulator = SPACE_ACCUMULATOR_BASE
        else:
            accumulator += SPACE_ACCUMULATOR_INCREMENT

        index += 1
    return text

def read_library(path):
    library = {}
    with io.open(path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            if line:
                a, b = line.split(":", 1)
                library[a] = b
    return library

def write_library(path, library):
    with io.open(path, "w", encoding="utf-8") as f:
        for key, value in library.items():
            f.write("{}:{}\n".format(key, value))

def main(lang, words):
    translator = Translator()
    dictionary = PyDictionary()

    # Load library
    lib_path = path_join(LIBRARY_FOLDER, lang)
    library_folder_exists = isdir(LIBRARY_FOLDER)
    library_exists = isfile(lib_path)

    if not library_folder_exists:
        print("'libraries' folder not detected, create at '{}'? (y/n)".format(path_join(getcwd(), LIBRARY_FOLDER)))
        prompt = input(">").lower()
        if prompt == 'y':
            mkdir(LIBRARY_FOLDER)
        else:
            exit("Libraries not available, shutting down.")

    if library_exists:
        library = read_library(lib_path)
    else:
        library = {}

    # Collect synonyms of words
    synonyms = []
    for word in words:
        synonyms += dictionary.synonym(word)

    synonyms = list(set(synonyms))  # Remove duplicates

    # Get translations of synonyms
    bulk = [s for s in synonyms if s not in library or library[s] == s]
    tls = translator.translate(bulk, dest=lang)
    """
    The google translator occasionally stops working, probably due to the questionably reverse engineering of the library
    This just makes it so that the library returns the original words as "translations"
    
    This bulk thing makes stuff a bit easier.
    """
    for i in range(len(tls)):
        library[synonyms[i]] = tls[i].text
    
    write_library(lib_path, library)
    collector = {library[s] for s in synonyms}    # We only care about the translations and not their meanings.
    # Filter out long outliers (circular expressions)
    lenlist = sorted([len(i) for i in list(collector)], reverse=True)
    while lenlist[0] > TL_OUTLIER*median(lenlist):
        l = lenlist.pop(0)
        collector = {i for i in collector if len(i) != l}

    # Randomly select chunks from translations
    chunks = []
    for tl in collector:
        while len(tl) >= CHUNK_MIN:
            chunk, tl = get_chunk(tl)
            chunks.append(chunk)

    names = []
    for _ in range(BATCH_SIZE):
        name = ""
        for _ in range(min(CHUNKS_MAX, max(CHUNK_MIN, round(normalvariate(CHUNKS_MEAN, CHUNKS_STD))))):
            name += choice(chunks)
        names.append(name)

    # Add spaces
    names = [add_space(name) for name in names]

    # Capitalize the first letter.
    names = [" ".join(word[0].upper()+word[1:].lower() for word in name.split()) for name in names]

    # Present from shortest to longest.
    names.sort(key=lambda x: len(x))
    for name in names:
        print(name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate names based on foreign words")
    parser.add_argument("lang", type=str, help="Language to translate to (de, fr)")
    parser.add_argument("words", type=str, nargs="+", help="Words to do")
    args = parser.parse_args()
    main(args.lang, args.words)