def remove_key_by_value(dictonary, value) -> []:
    return [i for i in dictonary if (i['name'] != value)]


def read_tags() -> list:
    with open("files/tags.txt") as file:
        tags = file.read().lower().split('\n')
    return tags


def is_categories_allowed(categories: [str]) -> bool:
    allowed = read_tags()
    return all(item in allowed for item in categories)
