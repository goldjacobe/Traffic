from enum import IntEnum, unique
import random
from datetime import datetime

block_length = 5  # units, includes one intersection
unit_length = 50  # feet, intersection length is always one unit
mean_driving_speed = 50  # feet per second
std_driving_speed = 20  # feet per second, for manually-driven cars
mean_int_time = 10  # seconds
std_int_time = 3  # seconds
grid_size = 5  # vary between 3,4,5
car_length = 20  # feet including buffer between cars
num_lanes = 3  # vary between 1,2,3
max_cars_allowed = 2
self_driving = True  # vary between True and False
array_size = (grid_size - 1) * block_length + 1
max_total_cars = 30  # vary between 10 - 30 in 5 car increments


@unique
class CityMap(IntEnum):
    empty = 0
    inter = 1
    vertical = 2
    horizontal = 3
    enter = 4
    exit = 5


class Interstate:
    def __init__(self, l):
        self.l = l

    def is_allowed(self, fr, to):
        return (fr, to) in self.l


class Intersection:
    intersections = {}

    def populate_states(self):
        if self.dirs == 3:
            self.states.append(Interstate([(180, 90), (270, 0)]))
        elif self.dirs == 5:
            self.states.append(Interstate([(0, 0), (180, 180)]))
        elif self.dirs == 6:
            self.states.append(Interstate([(0, 90), (270, 180)]))
        elif self.dirs == 9:
            self.states.append(Interstate([(180, 270), (90, 0)]))
        elif self.dirs == 10:
            self.states.append(Interstate([(90, 90), (270, 270)]))
        elif self.dirs == 12:
            self.states.append(Interstate([(0, 270), (90, 180)]))
        elif self.dirs == 7:
            self.states.append(Interstate([(0, 0), (180, 180), (0, 90)]))
            self.states.append(Interstate([(180, 90), (270, 0)]))
            self.states.append(Interstate([(270, 0), (270, 180)]))
        elif self.dirs == 11:
            self.states.append(Interstate([(90, 90), (270, 270), (270, 0)]))
            self.states.append(Interstate([(90, 0), (180, 270)]))
            self.states.append(Interstate([(180, 270), (180, 90)]))
        elif self.dirs == 13:
            self.states.append(Interstate([(0, 0), (180, 180), (180, 270)]))
            self.states.append(Interstate([(0, 270), (90, 180)]))
            self.states.append(Interstate([(90, 0), (90, 180)]))
        elif self.dirs == 14:
            self.states.append(Interstate([(90, 90), (270, 270), (90, 180)]))
            self.states.append(Interstate([(270, 180), (0, 90)]))
            self.states.append(Interstate([(0, 90), (0, 270)]))

        elif self.dirs == 15:
            self.states.append(Interstate([(0, 0), (180, 180), (0, 90),
                                           (180, 270)]))
            self.states.append(Interstate([(90, 0), (270, 180)]))
            self.states.append(Interstate([(90, 90), (270, 270), (90, 180),
                                           (270, 0)]))
            self.states.append(Interstate([(0, 270), (180, 90)]))

    def __init__(self, city_map, row, col):
        self.state_length = int(random.gauss(mean_int_time, std_int_time))
        self.cur_time = 0
        self.dirs = 0
        self.num_cars = 0
        if row > 0 and int(city_map[row - 1][col]) == 2:
            self.dirs += 1
        if col < array_size - 1 and int(city_map[row][col + 1]) == 3:
            self.dirs += 2
        if row < array_size - 1 and int(city_map[row + 1][col]) == 2:
            self.dirs += 4
        if col > 0 and int(city_map[row][col - 1]) == 3:
            self.dirs += 8
        if self_driving:
            self.num_cars = 0
        else:
            self.states = []
            self.populate_states()
            self.state = 0
        Intersection.intersections[(row, col)] = self

    def go(self):
        self.cur_time += 1
        if (self.cur_time / 1000) == self.state_length:
            self.state += 1
            self.state %= len(self.states)
            self.cur_time = 0

    def is_allowed(self, fr, to):
        return self.states[self.state].is_allowed(fr, to)

    def possible_directions(self, car):
        out = []
        if self.dirs % 2 == 1:
            out.append(0)
        if (self.dirs // 2) % 2 == 1:
            out.append(90)
        if (self.dirs // 4) % 2 == 1:
            out.append(180)
        if (self.dirs // 8) % 2 == 1:
            out.append(270)
        out.remove((car.direction + 180) % 360)
        return out


class Car:
    cars = []
    total_distance_travelled = 0
    total_time = 0

    @staticmethod
    def get_average_speed():
        return Car.total_distance_travelled / Car.total_time * 1000

    @staticmethod
    def enter_inter2(x, y):
        row = int(y / unit_length)
        col = int(x / unit_length)
        i = Intersection.intersections[(row, col)]
        if i.num_cars > max_cars_allowed:
            return False, i
        i.num_cars += 1
        return True, i

    @staticmethod
    def enter_inter(x, y, fr, to):
        if self_driving:
            return Car.enter_inter2(x, y)
        row = int(y // unit_length)
        col = int(x // unit_length)
        i = Intersection.intersections[(row, col)]
        return i.is_allowed(fr, to), i

    def __init__(self, city_map):
        start_point = int(random.random() * 2)
        if start_point == 0:
            self.direction = 90 * (int(random.random() * 2) + 1)
            if self.direction == 90:
                self.x = unit_length
                self.y = unit_length - 1
            else:
                self.x = 1
                self.y = unit_length
            self.ir = 0
            self.ic = 0
        else:
            self.direction = (90 * (int(random.random() * 2) + 1) + 180) % 360
            if self.direction == 0:
                self.x = unit_length * array_size - 1
                self.y = unit_length * (array_size - 1) - 1
            else:
                self.x = unit_length * (array_size - 1) - 1
                self.y = unit_length * (array_size - 1) + 1
            self.ir = array_size - 1
            self.ic = array_size - 1
        self.i = None
        self.next_dir = self.decide_next_dir()
        self.speed = random.gauss(mean_driving_speed, std_driving_speed)
        self.dist = self.speed / 1000
        self.time_in_inter = 0
        self.in_inter = False
        self.total_inter_time = int(unit_length / self.speed * 1000)
        self.city_map = city_map
        Car.cars.append(self)

    def get_square_type(self):
        row = int(self.y / unit_length)
        col = int(self.x / unit_length)
        return int(self.city_map[row][col])

    def decide_next_dir(self):
        self.ir = int(self.y / unit_length)
        self.ic = int(self.x / unit_length)
        row = self.ir
        col = self.ic
        if self.direction == 0:
            row -= 1
        elif self.direction == 90:
            col += 1
        elif self.direction == 180:
            row += 1
        elif self.direction == 270:
            col -= 1
        while (row, col) not in Intersection.intersections.keys():
            if self.direction == 0:
                row -= 1
            elif self.direction == 90:
                col += 1
            elif self.direction == 180:
                row += 1
            elif self.direction == 270:
                col -= 1
            if (row, col) == (0, 0) or (row, col) == (array_size - 1,
                                                      array_size - 1):
                return self.direction
        inter = Intersection.intersections[(row, col)]
        self.i = inter
        dirs = inter.possible_directions(self)
        if self.direction in dirs:
            dirs.append(self.direction)
        ind = int(random.random() * len(dirs))
        return dirs[ind]

    def go(self):
        Car.total_time += 1
        if self.in_inter:
            self.time_in_inter += 1
            Car.total_distance_travelled += self.dist
            if self.time_in_inter == self.total_inter_time:
                self.direction = self.next_dir
                self.next_dir = self.decide_next_dir()
                self.in_inter = False
                self.time_in_inter = 0
                self.i.num_cars -= 1
            return

        hit = 0
        for c in Car.cars:
            if c is self or c.in_inter:
                continue
            if would_hit(self.direction, self.x, self.y, c.direction, c.x, c.y):
                hit += 1
        if hit >= num_lanes:
            return

        old_x = self.x
        old_y = self.y
        if self.direction == 0:
            self.y -= self.dist
        elif self.direction == 90:
            self.x += self.dist
        elif self.direction == 180:
            self.y += self.dist
        else:
            self.x -= self.dist
        if self.get_square_type() == 1:
            (b, self.i) = Car.enter_inter(self.x, self.y, self.direction,
                                          self.next_dir)
            if b:
                self.ir = int(self.y / unit_length)
                self.ic = int(self.x / unit_length)
                self.in_inter = True
                row = self.ir
                col = self.ic
                if self.next_dir == 0:
                    self.x = unit_length * (col + 1) - 1
                    self.y = unit_length * row - 1
                elif self.next_dir == 90:
                    self.x = unit_length * (col + 1) + 1
                    self.y = unit_length * (row + 1) - 1
                elif self.next_dir == 180:
                    self.x = unit_length * col + 1
                    self.y = unit_length * (row + 1) + 1
                else:
                    self.x = unit_length * col - 1
                    self.y = unit_length * row + 1
                    Car.total_distance_travelled += self.dist
            else:
                self.x = old_x
                self.y = old_y
                return

        Car.total_distance_travelled += self.dist

        t = self.get_square_type()
        if t == 1:
            self.in_inter = True

        if t == 4 or t == 5:
            Car.cars.remove(self)
            del self


def would_hit(direct1, x1, y1, direct2, x2, y2):
    if direct1 != direct2:
        return False
    if (direct1 == 0 and x1 == x2 and abs(y1 - y2) < car_length and y1 > y2) or (direct1 == 90 and y1 == y2 and abs(x1 - x2) < car_length and x1 < x2) or (direct1 == 180 and x1 == x2 and abs(y1 - y2) < car_length and y1 < y2) or (direct1 == 270 and y1 == y2 and abs(x1 - x2) < car_length and x1 > x2):
        return True
    return False


def main():
    random.seed(datetime.now())
    city_map = [[CityMap.empty for j in range(array_size)] for i in range(
        array_size)]

    for i in range(array_size):
        for j in range(array_size):
            if i == 0 and j == 0:
                city_map[i][j] = CityMap.enter
            elif i == array_size - 1 and j == array_size - 1:
                city_map[i][j] = CityMap.exit
            elif i % block_length == 0 and j % block_length == 0:
                city_map[i][j] = CityMap.inter
            elif i % block_length == 0:
                city_map[i][j] = CityMap.horizontal
            elif j % block_length == 0:
                city_map[i][j] = CityMap.vertical

    for i in range(array_size):
        for j in range(array_size):
            if int(city_map[i][j]) == 1:
                Intersection(city_map, i, j)

    time = 0  # milliseconds
    while time < 100000:  # main loop
        if time % 1000 == 0 and len(Car.cars) < max_total_cars:
            Car(city_map)
        for c in Car.cars:
            c.go()
        if not self_driving:
            for i in Intersection.intersections.values():
                i.go()
        time += 1
    print(Car.get_average_speed())


def test():
    pass

if __name__ == "__main__":
    main()