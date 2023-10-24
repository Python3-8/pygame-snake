# import sys
# import pprint
import random
from enum import Enum, auto
import pygame

# globals
scrw, scrh = 600, 600
bg_color = 0, 0, 0
snakew, snakeh = 20, 20
snake_color = 255, 255, 255
head_color = 255, 255, 255
head_brightness = 0.8
foodw, foodh = snakew * 0.75, snakeh * 0.75
food_color = 255, 255, 0
speed = snakew
fps = speed // 2 + 2

# classes


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    RIGHT = auto()
    LEFT = auto()

    def get_velocity(self) -> tuple[int | float]:
        match self:
            case Direction.UP:
                return (0, -speed)
            case Direction.DOWN:
                return (0, speed)
            case Direction.RIGHT:
                return (speed, 0)
            case Direction.LEFT:
                return (-speed, 0)


class SnakePart:
    def __init__(self, pos: tuple[int | float], direction: Direction):
        self._id = random.random()
        self._pos = pos
        self._direction = direction
        self._velocity = self._direction.get_velocity()

    @property
    def id(self) -> float:
        return self._id

    @property
    def x(self) -> float:
        return self._pos[0] - snakew / 2

    @property
    def y(self) -> float:
        return self._pos[1] - snakeh / 2

    @property
    def pos(self) -> tuple[float]:
        return self.x, self.y

    @property
    def virtual_pos(self) -> tuple[float]:
        return self._pos

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def velocity(self) -> tuple[int | float]:
        return self._velocity

    @property
    def rect(self) -> tuple[int | float]:
        return self.x, self.y, snakew, snakeh

    @property
    def successor(self):
        match self._direction:
            case Direction.UP:
                pos = self._pos[0], self._pos[1] + snakeh
            case Direction.DOWN:
                pos = self._pos[0], self._pos[1] - snakeh
            case Direction.RIGHT:
                pos = self._pos[0] - snakew, self._pos[1]
            case Direction.LEFT:
                pos = self._pos[0] + snakew, self._pos[1]
        return SnakePart(pos, self._direction)

    def change_direction(self, new_direction: Direction):
        self._direction = new_direction
        self._velocity = self._direction.get_velocity()

    def move(self):
        new_pos = [self._pos[0] + self._velocity[0],
                   self._pos[1] + self._velocity[1]]
        if new_pos[0] < 0:
            new_pos[0] = scrw - snakew
        if new_pos[0] > scrw - snakew:
            new_pos[0] = 0
        if new_pos[1] < 0:
            new_pos[1] = scrh - snakeh
        if new_pos[1] > scrh - snakeh:
            new_pos[1] = 0
        self._pos = tuple(new_pos)


class Food:
    def __init__(self, pos: tuple[int | float]):
        self._pos = pos

    @property
    def x(self) -> float:
        return self._pos[0] - foodw / 2

    @property
    def y(self) -> float:
        return self._pos[1] - foodh / 2

    @property
    def pos(self) -> tuple[float]:
        return self.x, self.y

    @property
    def virtual_pos(self) -> tuple[float]:
        return self._pos

    @property
    def rect(self) -> tuple[int | float]:
        return self.x, self.y, foodw, foodh

    @classmethod
    def spawn(cls):
        return cls((random.randint(snakew, scrw - snakew), random.randint(snakeh, scrh - snakeh)))


class DirectionChange:
    def __init__(self, virtual_pos: tuple[int | float], to: Direction):
        self._virtual_pos, self._to = virtual_pos, to
        self._changed_ids: list[float] = []

    def __repr__(self):
        return f'[DirectionChange to {self._to} at {self._virtual_pos}]'

    @property
    def virtual_pos(self):
        return self._virtual_pos

    @property
    def to(self):
        return self._to

    @property
    def changed_ids(self):
        return self._changed_ids

    def already_changed(self, snake_part: SnakePart):
        return snake_part.id in self._changed_ids

    def add_changed(self, snake_part: SnakePart):
        self._changed_ids.append(snake_part.id)


# initialize game
pygame.init()
scr = pygame.display.set_mode((scrw, scrh))
pygame.display.set_caption('Pygame Snake')
clock = pygame.time.Clock()

# variables
head = SnakePart((scrw / 2, scrh / 2), Direction.UP)
food = Food.spawn()
snake_parts: list[SnakePart] = [head]
# queue of direction changes and their positions
direction_changes: tuple[DirectionChange] = ()


def grow():
    snake_parts.append(snake_parts[-1].successor)


def brightness(color: tuple[int], brightness: float):
    return tuple(brightness * color_value for color_value in color)


# mainloop
run = True
paused = False
while run:
    clock.tick(fps)
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if not paused:
                head_direction = head.direction
                if head_direction not in (Direction.UP, Direction.DOWN) and event.key == pygame.K_UP:
                    direction_changes += DirectionChange(
                        head.virtual_pos, Direction.UP),
                elif head_direction not in (Direction.UP, Direction.DOWN) and event.key == pygame.K_DOWN:
                    direction_changes += DirectionChange(
                        head.virtual_pos, Direction.DOWN),
                elif head_direction not in (Direction.RIGHT, Direction.LEFT) and event.key == pygame.K_RIGHT:
                    direction_changes += DirectionChange(
                        head.virtual_pos, Direction.RIGHT),
                elif head_direction not in (Direction.RIGHT, Direction.LEFT) and event.key == pygame.K_LEFT:
                    direction_changes += DirectionChange(
                        head.virtual_pos, Direction.LEFT),
                # elif event.key == pygame.K_a:
                #     grow()
                # sys.stdout.write(f'{len(direction_changes)}: ')
                # pprint.pprint(direction_changes)
                # sys.stdout.flush()
    if not paused:
        scr.fill(bg_color)
        # drawing food
        food_rect = pygame.draw.rect(scr, food_color, food.rect)
        # drawing snake
        body_rects = ()
        for index, snake_part in enumerate(snake_parts):
            virtual_pos = snake_part.virtual_pos
            remove_direction_changes = ()
            for direction_change in direction_changes:
                if virtual_pos == direction_change.virtual_pos and not direction_change.already_changed(snake_part):
                    snake_part.change_direction(direction_change.to)
                    direction_change.add_changed(snake_part)
                    if index == len(snake_parts) - 1:
                        # this is the last snake part
                        remove_direction_changes += direction_change,
            direction_changes = tuple(
                direction_change for direction_change in direction_changes if direction_change not in remove_direction_changes)
            snake_part.move()
            if index == 0:
                snake_part_rect = pygame.draw.rect(
                    scr, brightness(head_color, head_brightness), snake_part.rect)
                head_rect = snake_part_rect
            else:
                snake_part_rect = pygame.draw.rect(
                    scr, snake_color, snake_part.rect)
                body_rects += snake_part_rect,
        if head_rect.colliderect(food_rect):
            food = Food.spawn()
            grow()
        elif head_rect.collidelist(body_rects) != -1:
            # snake has collided with itself
            run = False
        pygame.display.update()

pygame.quit()
