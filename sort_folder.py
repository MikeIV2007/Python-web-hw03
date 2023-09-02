import os
from pathlib import Path
import zipfile
import uuid
import time
from threading import Thread
import logging

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


CATEGORIES = {
    "Images": [".jpeg", ".png", ".jpg", ".svg"],
    "Video": [".avi", ".mp4", ".mov", ".mkv", ".wmv"],
    "Documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx"],
    "Music": [".mp3", ".ogg", ".wav", ".amr"],
    "Archives": [".zip", ".gz", ".tar"],
    "Unkknown": [],
}

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = (
    "a",
    "b",
    "v",
    "g",
    "d",
    "e",
    "e",
    "j",
    "z",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "r",
    "s",
    "t",
    "u",
    "f",
    "h",
    "ts",
    "ch",
    "sh",
    "sch",
    "",
    "y",
    "",
    "e",
    "yu",
    "ya",
    "je",
    "i",
    "ji",
    "g",
)

TRANS = {}

for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


def normalize(text: str) -> str:
    text = text.translate(TRANS)
    for chr in text:
        if ord(chr) in range(48, 58):
            continue
        elif ord(chr) in range(65, 91):
            continue
        elif ord(chr) in range(97, 123):
            continue
        else:
            text = text.replace(chr, "_")
    return text


def delete_empty_folders(path: Path) -> None:
    for root, dirs, files in os.walk(path, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)

            if not os.listdir(folder_path):
                os.rmdir(folder_path)


def move_file(file: Path, root_dir: Path, category: str) -> None:
    target_dir = root_dir.joinpath(category)

    if not target_dir.exists():
        target_dir.mkdir()

    new_file_name = target_dir.joinpath(f"{normalize(file.stem)}{file.suffix}")

    if new_file_name.exists():
        new_file_name = new_file_name.with_name(
            f"{new_file_name.stem}-{uuid.uuid4()}{file.suffix}"
        )

    file.rename(new_file_name)


def get_categories(file: Path) -> str:
    ext = file.suffix.lower()

    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    cat = "Unknown"
    return cat


def sort_folder(path: Path, destination_path: Path) -> None:
    for item in path.glob("**/*"):
        if item.is_file():
            category = get_categories(item)
            move_file(item, destination_path, category)


def unzip_archives(path: Path) -> None:
    path_archives = os.path.join(path, "Archives")

    if os.path.exists(path_archives):
        for i in os.listdir(path_archives):
            file_extension = list(os.path.splitext(i))
            folder_name = file_extension[0]

            extraction_path = os.path.join(path_archives, folder_name)

            if not os.path.exists(extraction_path):
                os.makedirs(extraction_path)

            with zipfile.ZipFile(os.path.join(path_archives, i), "r") as zip_ref:
                zip_ref.extractall(extraction_path)


def print_lists(path: Path) -> list:
    for item in path.glob("**/*"):
        if item.is_dir():
            file_list = []
            category_name = item.name

            for file in item.glob("*"):
                file_list.append(file.name)
            print(f"\nList of {category_name} : {file_list}\n")


def print_all_exrentions(path: Path) -> list:
    all_ext_set = set()

    for item in path.glob("**/*"):
        if item.is_file():
            ext = item.suffix
            all_ext_set.add(ext)
    all_ext_list = list(all_ext_set)
    print(f"\nList of all found extentions  :  {all_ext_list}\n")


def get_pass():
    try:
        user_input = input(
            '\nSORTER: Enter valid path to folder or enter "exit" to leave programm \n>>>'
        )

        if user_input == "exit":
            print("End of programm!\n")
            return exit()
        if user_input == "":
            print("\nPath cannot be empty!")
            return get_pass()

        path = Path(user_input)
    except IndexError:
        return print("There is no path to folder! Enter path!")

    if not path.exists():
        return print(f"The path <<< {path} >>> doesn't exist! Enter valid path!")
    return path


def main():
    logging.debug("\nProgramm Started")

    start_timer = time.perf_counter()

    user_path = get_pass()

    items = os.listdir(user_path)

    threads = []
    i = 1
    for item in items:
        item_path = os.path.join(user_path, item)
        item_path = Path(item_path)
        if os.path.isdir(item_path):
            thread = Thread(
                name=f"thread0{i}", target=sort_folder, args=(item_path, user_path)
            )
            logging.debug(f"{thread.name} Started")
            i += 1
            threads.append(thread)
            thread.start()

        else:
            category = get_categories(item_path)
            move_file(item_path, user_path, category)

    for thread in threads:
        thread.join()

    delete_empty_folders(user_path)
    print_lists(user_path)
    print_all_exrentions(user_path)
    unzip_archives(user_path)

    finish = time.perf_counter()
    logging.debug(f"\nProgramm finished in {finish-start_timer} seconds\n")


if __name__ == "__main__":
    main()
