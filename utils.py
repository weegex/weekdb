import os
import random


class SearchError(Exception):
    ...


def is_type(object: any, type: any) -> any:
    if isinstance(object, type):
        return object
    raise TypeError(
        f"expected {type.__name__}, received {object.__class__.__name__}")


class Path:
    def __init__(self, path: str) -> None:
        self.__path: str = is_type(path, str)
        if not os.path.isfile(self.__path) and self.__path.endswith(".json"):
            raise FileNotFoundError("file does not match json extension")

    def get(self):
        return self.__path


def str_to_int(string: str):
    letters = []

    for letter in is_type(string, str):
        letters.append(str(ord(letter)))

    return int("".join(letters))


def binary_search_document(array: list, key: any):
    ids_array = []

    for index, item in enumerate(is_type(array, list)):
        id = item.get("_id")

        if not isinstance(id, int):
            id = str_to_int(str(id))

        ids_array.append([id, index])

    sorted_array = sorted(ids_array, key=lambda x: x[0])

    if not isinstance(key, int):
        key = str_to_int(str(key))

    low = 0
    high = len(sorted_array) - 1

    while low <= high:

        middle = (low + high) // 2
        middle_item = sorted_array[middle][0]

        if middle_item == key:
            return sorted_array[middle][1]
        elif middle_item > key:
            high = middle - 1
        else:
            low = middle + 1

    raise SearchError("document does not exist")


def generate_random_key():
    letters = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&"
    part1 = ''.join(random.choice(letters)
                    for i in range(random.randint(10, 20)))
    part2 = ''.join(random.choice(letters)
                    for i in range(random.randint(20, 40)))
    part3 = ''.join(random.choice(letters)
                    for i in range(random.randint(30, 60)))

    return part1 + "///" + part2 + "///" + part3
