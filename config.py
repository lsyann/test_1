from sys import argv
from typing import Any


class Zone:
    def __init__(self, name: str, x: int, y: int,
            color: str, connections: list = [],
            nb_drone: int = -1, start: bool = False,
            end: bool = False, max_drone: int = -1,
            status: str = "", current_drone: list = []) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.start = start
        self.end = end
        self.max_drone = max_drone
        self.connections = connections
        self.nb_drone = nb_drone
        self.status = status
        self.current_drone = current_drone


def get_nb(line: str) -> tuple[str, int]:
    i = 0
    nb = ""
    while ((line[i].isnumeric() or line[i] == "-") and i < len(line)):
        nb += line[i]
        i += 1
    line = line[i:].strip()
    return (line, int(nb))


def parse_hub(line: str) -> Zone:
    start = False
    end = False
    if line.startswith("start_hub:"):
        start = True
        line = line[10:]
    elif line.startswith("end_hub:"):
        end = True
        line = line[8:]
    else:
        line = line[4:]
    line = line.strip()
    name = ""
    i = 0
    while (line[i] != " " and i < len(line)):
        name += line[i]
        i += 1
    if "-" in name:
        raise Exception(f"Invalid zone name: {name}")
    line = line[i:].strip()
    temp = get_nb(line)
    line = temp[0]
    x = temp[1]
    temp = get_nb(line)
    line = temp[0]
    y = temp[1]
    if line[0] != '[' or line[-1] != ']':
        raise Exception(f"Invalid options: {line}")
    line = line[1:]
    i = 0
    color = ""
    nb = ""
    zone_status = ""
    max_drones = ""
    while line[i] != "]":
        opt = ""
        while line[i] != '=':
            opt += line[i]
            i += 1
        i += 1
        if opt == "color":
            if color != "":
                raise Exception("same option twice")
            while line[i] != " " and line[i] != "]":
                color += line[i]
                i += 1
            if color == "darkred" or color == "maroon" or color == "gold" or color == "crimson" or color == "rainbow":
                color = "red"
        elif opt == "zone":
            if zone_status != "":
                raise Exception("same option twice")
            while line[i] != " " and line[i] != "]":
                zone_status += line[i]
                i += 1
        elif opt == "max_drones":
            if type(max_drones) is int:
                raise Exception("same option twice")
            while line[i] == "-" or line[i].isdigit():
                nb += line[i]
                i += 1
            nb = int(nb)
        if line[i] == " ":
            i += 1
    if color == "":
        raise Exception(f"Missing mandator param 'color'")
    zone = Zone(name=name, x=x, y=y, color=color, start=start, end=end, max_drone=max_drones, connections=[], current_drone=[])
    if zone_status != "":
        zone.status = zone_status
    if type(nb) is int:
        zone.max_drone = nb
    return zone


def get_connection(line: str, lst: list[Zone]) -> list[Zone]:
    if "-" not in line:
        return lst
    first, second = "", ""
    nb = -1
    i = 0
    while line[i] != "-":
        first += line[i]
        i += 1
    i += 1
    while i < len(line) and line[i] != " ":
        second += line[i]
        i += 1
    line = line[len(second) + len(first) + 1:].strip()
    if len(line) != 0:
        if not line.startswith("[max_link_capacity") or line[-1] != "]" or "=" not in line:
            raise Exception(f"invalid connection option: {line}")
        line = line[18:].strip()
        if line[0] != "=":
            raise Exception(f"invalid connection option: {line}")
        line = line[1:].strip()
        nb = ""
        i = 0
        while line[i].isnumeric():
            nb += line[i]
            i += 1
        nb = int(nb)
    names = [elem.name for elem in lst]
    if first != second and first in names and second in names:
        for elem in lst:
            if elem.name == second and first not in elem.connections:
                elem.connections.append((first, nb))
            elif elem.name == first and second not in elem.connections:
                elem.connections.append((second, nb))
    else:
        raise Exception(f"Invalid connection: {first, second}")
    return lst


def parse_config(lst: list[str]) -> list[Zone]:
    final = []

    if not lst[0].startswith("nb_drones: "):
        raise Exception("Invalid file")

    lst[0] = lst[0][11:]

    if not lst[0].isnumeric():
        raise Exception("Invalid number of drones")

    nb = int(lst[0])
    for elem in lst:
        if elem.startswith("start_hub:") or elem.startswith("end_hub:") or (
                elem.startswith("hub:")):
            final.append(parse_hub(elem))

    i = 0
    for i in range(len(lst)):
        if lst[i].startswith("connection:"):
            final = get_connection(lst[i][11:].strip(), final)
    for elem in final:
        elem.nb_drone = nb
        #print(elem.__dict__)
    return final


def get_config() -> None:
    try:
        if len(argv) != 2:
            raise Exception("Wrong argument count")
        lst = []
        with open(argv[1]) as file:
            for line in file:
                line = line.strip()
                line = line.replace("\n", "")
                if line != "" and line[0] != '#':
                    lst.append(line)
        lst = parse_config(lst)
    except Exception as err:
        print(err)
        return
    return lst
