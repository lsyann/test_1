from config import Zone


def get_elem(name: str, lst: list[Zone]) -> Zone:
    for elem in lst:
        if elem.name == name:
            return elem
    return None


class Drone:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_path(self, lst_map: list[Zone],
                 path: list = [], previous: list = []) -> tuple[int, int]:
        if self.name in previous:
            return []
        previous.append(self.name)
        for elem in lst:
            if elem.end is True:
                end = elem
        all_paths = []
        i = 0
        for elem in self.connections:
            if get_elem(elem[1], lst).max_drones < len(get_elem(elem[1], lst)):
                path.append(elem)
                path = get_path(elem, lst_map, path, previous)
            return path
