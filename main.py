from config import get_config
from drones import Drone
import pygame as pg


def main() -> None:
    config = get_config()
    if config is None or len(config) == 0:
        return

    max_x, max_y = 0, 0
    min_x, min_y = 0, 0

    for elem in config:
        if elem.x > max_x:
            max_x = elem.x
        if elem.y > max_y:
            max_y = elem.y
        if elem.x < min_x:
            min_x = elem.x
        if elem.y < min_y:
            min_y = elem.y
        if elem.start is True:
            for i in range(elem.nb_drone):
                elem.current_drone.append(Drone(elem.x, elem.y))
    min_x, min_y = -min_x, -min_y

    lst = []

    width = CS * (max_x + min_x + 1) + 20
    height = CS * (max_y + min_y + 1) + 20

    pg.init()

    screen = pg.display.set_mode((width, height))
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        screen.fill("black")
        for i in range(len(config)):
            pg.draw.rect(screen, config[i].color, pg.Rect((config[i].x + min_x) * CS + 10, (config[i].y + min_y) * CS + 10, CS, CS))
            if config[i].current_drone != []:
                pg.draw.rect(screen, "white", pg.Rect((config[i].x + min_x + 0.25) * CS + 10, (config[i].y + min_y + 0.25) * CS + 10, CS / 4, CS / 4))

        pg.display.flip()


CS = 80
main()
