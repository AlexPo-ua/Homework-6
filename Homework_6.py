import collections
import shutil
import sys
from pathlib import Path

# Cловник, згідно якого визначаються правила сортування файлів:
# ключі - папки;
# значення - список розширеннь файлів, які потрібно в ці папки перемістити.
file_categories_dict = {
    "documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pttx"],
    "audio": [".mp3", ".ogg", ".wav", ".amr"],
    "video": [".avi", ".mp4", ".mov", ".mkv"],
    "images": [".jpeg", ".png", ".jpg", ".svg"],
    "archives": [".zip", ".gz", ".tar"],
}

# Правило транслітерації назв файлів на латинські та безпечні символи:
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ?<>,!@#[]#$%^&*()-=; "
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
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
)
TRANS = {}
for cyrillic_symbol, translated_symbol in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(cyrillic_symbol)] = translated_symbol
    TRANS[ord(cyrillic_symbol.upper())] = translated_symbol.upper()


def normalize(name):
    """Функція замінює кирилічні символи на латинські"""
    global TRANS
    return name.translate(TRANS)


def is_file_exists(file, dir):
    """Функція перевіряє, чи вже існує файл з такою назвою.
    Якщо існує, то добавляє до назви круглих дужках число 1"""
    if file in dir.iterdir():
        add_name = "1"
        name = file.resolve().stem + f"({add_name})" + file.suffix
        file_path = Path(dir, name)
        return file_path
    return file


def is_fold_exists(file, dir):
    """Функція перевіряє чи існує необхідна папка, якщо немає - створює її"""
    if dir.exists():
        folder_sort(file, dir)
    else:
        Path(dir).mkdir()
        folder_sort(file, dir)


def folder_sort(file, dir):
    """Функція змінює назву файла та переміщає в необхідну папку."""
    latin_name = normalize(file.name)
    new_file = Path(dir, latin_name)
    file_path = is_file_exists(new_file, dir)
    file.replace(file_path)


def sort_file(folder, p):
    """Функція перевіряє кожну папку та файли по їх розширенню, організовує сортування файлів, та зміну їх назв"""
    for i in p.iterdir():
        if i.name in (
            "documents",
            "audio",
            "video",
            "images",
            "archives",
            "other",
        ):
            continue
        if i.is_file():
            flag = False
            for f, suf in file_categories_dict.items():
                if i.suffix.lower() in suf:
                    dr = Path(folder, f)
                    is_fold_exists(i, dr)
                    flag = True
                else:
                    continue
            if not flag:
                dr = Path(folder, "other")
                is_fold_exists(i, dr)
        elif i.is_dir():
            if len(list(i.iterdir())) != 0:
                sort_file(folder, i)
            else:
                shutil.rmtree(i)
        for j in p.iterdir():
            if j.name == "archives" and len(list(j.iterdir())) != 0:
                for arch in j.iterdir():
                    if arch.is_file() and arch.suffix in (".zip", ".gz", ".tar"):
                        try:
                            arch_dir_name = arch.resolve().stem
                            path_to_unpack = Path(folder, "archives", arch_dir_name)
                            shutil.unpack_archive(arch, path_to_unpack)
                        except:
                            print(f"Увага! Помилка розпаковки архіву! '{arch.name}'!\n")
                        finally:
                            continue
                    else:
                        continue
            elif j.is_dir() and not len(list(j.iterdir())):
                shutil.rmtree(j)


def show_result(p):
    total_dict = collections.defaultdict(list)
    files_dict = collections.defaultdict(list)

    for item in p.iterdir():
        if item.is_dir():
            for file in item.iterdir():
                if file.is_file():
                    total_dict[item.name].append(file.suffix)
                    files_dict[item.name].append(file.name)
    for k, v in files_dict.items():
        print()
        print(f"Папка '{k}' включає файли:")
        print(f"--- {v}")

    print()
    print("*** Сортування файлів завершено! ***")
    print("---------------------------------------------------------------------------")
    print(
        "| {:^11} |{:^18}| {:^19} ".format(
            "Папка", "Кількість файлів", "Розширення файлів"
        )
    )
    print("---------------------------------------------------------------------------")

    for key, value in total_dict.items():
        k, a, b = key, len(value), ", ".join(set(value))
        print("| {:<11} |{:^18}| {:<19} ".format(k, a, b))

    print(
        "----------------------------------------------------------------------------"
    )
    print()


def main(path):
    p = Path(path)
    folder = Path(path)
    try:
        sort_file(folder, p)
    except FileNotFoundError:
        print("Папка не знайдена. Перевірте шлях до папки та спробуйте ще раз.")
        return
    return show_result(p)


if __name__ == "__main__":
    if len(sys.argv) > 0:
        path = sys.argv[1]
        main(path)
    else:
        print("Не вказано шлях до папки")
