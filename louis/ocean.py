import sys
import random

directions = ["N", "W", "E", "S"]


class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_distance(self, position):
        return abs(self.x - position.x) + abs(self.y - position.y)

    def add_direction(self, direction):
        if direction == "N":
            return Position(self.x, self.y - 1)

        if direction == "W":
            return Position(self.x - 1, self.y)

        if direction == "S":
            return Position(self.x, self.y + 1)

        if direction == "E":
            return Position(self.x + 1, self.y)

    def add_position(self, position):
        return Position(
            x=self.x + position.x,
            y=self.y + position.y
        )

    def __str__(self):
        return "x: {} / y: {}".format(self.x, self.y)


class Ship(object):
    def __init__(self):
        self.position = Position(0, 0)
        self.direction = "N"
        self.torpedo_cooldown = 3

    def update_turn_data(self, turn_data):
        self.torpedo_cooldown = turn_data["torpedo_cooldown"]

    def move(self, direction):
        self.direction = direction
        self.position = self.position.add_direction(direction)

    def get_position_after_move(self, direction):
        return self.position.add_direction(direction)

    def choose_starting_cell(self, board):
        x = random.randint(0, board.width - 1)
        y = random.randint(0, board.height - 1)
        random_position = Position(x, y)
        while not board.is_position_valid_for_move(random_position):
            random_position.x = random.randint(0, board.width - 1)
            random_position.y = random.randint(0, board.height - 1)
        self.position = random_position
        print("{} {}".format(self.position.x, self.position.y))

    def __str__(self):
        return str(self.position)


class Cell(object):
    def __init__(self, position, is_island):
        self.position = position
        self.is_island = is_island
        self.is_visited = False
        self.can_be_enemy_start = not is_island
        self.can_be_enemy_position = not is_island

    def has_been_visited(self):
        self.is_visited = True

    def is_valid_for_move(self):
        return not (self.is_island or self.is_visited)

    def cannot_be_enemy_start(self):
        self.can_be_enemy_start = False

    def set_can_be_enemy_position(self, can_be_enemy_position):
        self.can_be_enemy_position = can_be_enemy_position

    def __str__(self):
        return "x" if self.is_island else "."

    def print_can_be_here(self):
        return "x" if not self.can_be_enemy_position else "."

    def reset_visit(self):
        self.is_visited = False


class Board(object):
    def __init__(self, height, width, lines):
        self.height = height
        self.width = width
        self.map = []
        for y, line in enumerate(lines):
            cell_line = []
            for x, char in enumerate(line):
                cell_line.append(Cell(Position(x, y), char == "x"))
            self.map.append(cell_line)

    def is_position_in_grid(self, position):
        if position.x < 0 or position.x >= self.width:
            return False
        if position.y < 0 or position.y >= self.height:
            return False
        return True

    def is_position_valid_for_move(self, position):
        if not self.is_position_in_grid(position):
            return False
        return self.get_cell(position).is_valid_for_move()

    def is_position_valid_for_enemy(self, position):
        if not self.is_position_in_grid(position):
            return False
        return not self.get_cell(position).is_island

    def get_cell(self, position):
        try:
            return self.map[position.y][position.x]
        except IndexError:
            return False

    def is_position_dead_end(self, position):
        available_direction = 0
        for direction in directions:
            new_position = position.add_direction(direction)
            if self.is_position_valid_for_move(new_position):
                available_direction += 1
        return available_direction == 0

    def update_enemy_start_position(self, delta_position):
        for x in range(self.width):
            for y in range(self.height):
                start_position = Position(x, y)
                current_position = start_position.add_position(delta_position)
                if not self.is_position_valid_for_enemy(current_position):
                    self.get_cell(start_position).cannot_be_enemy_start()

    def compute_number_of_potential_positions(self):
        number_of_positions = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.get_cell(Position(x,y)).can_be_enemy_position:
                    number_of_positions += 1
        return number_of_positions

    def update_enemy_current_position(self, delta_position):
        for x in range(self.width):
            for y in range(self.height):
                current_position = Position(x, y)
                start_position = current_position.add_position(
                    Position(
                        x=-1 * delta_position.x,
                        y=-1 * delta_position.y
                    )
                )
                if not self.get_cell(start_position):
                    self.get_cell(current_position).can_be_enemy_position = False
                else:
                    can_be_position = self.get_cell(start_position).can_be_enemy_start
                    self.get_cell(current_position).can_be_enemy_position = can_be_position

    def reset_is_visited(self):
        for x in range(self.width):
            for y in range(self.height):
                self.get_cell(Position(x=x, y=y)).reset_visit()

    def print_potential_position_board(self):
        for line in self.map:
            line_string = ""
            for cell in line:
                line_string += cell.print_can_be_here()
            ServiceUtils.print_log(line_string)


class EnemyShip(object):
    def __init__(self, height, width, lines):
        self.delta_position = Position(0, 0)
        self.enemy_board = Board(
            height=height,
            width=width,
            lines=lines
        )
        self.number_of_possible_positions = height * width

    def update_number_of_possible_positions(self):
        self.number_of_possible_positions = self.enemy_board.compute_number_of_potential_positions()

    def read_opponent_order(self, opponent_order):
        if opponent_order == "NA":
            return
        list_opponent_order = opponent_order.split("|")
        move_order = ServiceOrder.get_move_order(list_opponent_order)
        if move_order:
            self.delta_position = self.delta_position.add_direction(
                ServiceOrder.get_direction_from_order(move_order)
            )
        self.enemy_board.update_enemy_start_position(self.delta_position)
        self.enemy_board.update_enemy_current_position(self.delta_position)
        self.update_number_of_possible_positions()


class ServiceUtils:
    @staticmethod
    def print_log(log):
        print(log, file=sys.stderr)

    @staticmethod
    def read_turn_data():
        x, y, my_life, opp_life, torpedo_cooldown, \
        sonar_cooldown, silence_cooldown, \
        mine_cooldown = [int(i) for i in input().split()]
        sonar_result = input()
        opponent_orders = input()
        return {
            "x": x,
            "y": y,
            "my_life": my_life,
            "opp_life": opp_life,
            "torpedo_cooldown": torpedo_cooldown,
            "sonar_cooldown": sonar_cooldown,
            "silence_cooldown": silence_cooldown,
            "sonar_result": sonar_result,
            "opponent_orders": opponent_orders,
        }

    @staticmethod
    def read_global_data():
        width, height, my_id = [int(i) for i in input().split()]
        lines = []
        for i in range(height):
            lines.append(input())
        return {
            "width": width,
            "height": height,
            "lines": lines
        }

    @classmethod
    def init(cls):
        global_data = cls.read_global_data()
        board = Board(
            height=global_data["height"],
            width=global_data["width"],
            lines=global_data["lines"]
        )
        ennemy_ship = EnemyShip(
            height=global_data["height"],
            width=global_data["width"],
            lines=global_data["lines"]
        )

        my_ship = Ship()
        my_ship.choose_starting_cell(
            board=board
        )
        return global_data, board, ennemy_ship, my_ship


class ServiceMovement:
    @staticmethod
    def is_move_possible_in_direction(ship, direction, board):
        next_position = ship.get_position_after_move(direction)
        return board.is_position_valid_for_move(next_position)

    @staticmethod
    def move_my_ship(ship, direction, board):
        board.get_cell(position=ship.position).has_been_visited()
        ship.move(direction)
        move_order = ServiceOrder.create_move_order(direction)
        return move_order

    @staticmethod
    def random_direction():
        return random.choice(directions)

    @classmethod
    def chose_movement_and_move(cls, ship, board):
        if board.is_position_dead_end(ship.position):
            return False
        direction = cls.random_direction()
        while not cls.is_move_possible_in_direction(ship, direction, board):
            direction = cls.random_direction()
        move_order = cls.move_my_ship(ship, direction, board)
        return move_order

    @staticmethod
    def surface(board):
        board.reset_is_visited()
        return "SURFACE"


class ServiceOrder:
    @staticmethod
    def get_move_order(list_orders):
        for order in list_orders:
            if order.find("MOVE") > -1:
                return order
        return False

    @staticmethod
    def get_direction_from_order(move_order):
        return move_order.replace("MOVE ", "")

    @staticmethod
    def concatenate_order(list_orders):
        filtered_list = list(filter(lambda order: order, list_orders))
        return "|".join(filtered_list)

    @staticmethod
    def display_order(order):
        print(order)

    @staticmethod
    def create_move_order(direction):
        return "MOVE {} TORPEDO".format(direction)

    @staticmethod
    def create_msg_order(msg):
        return "MSG {}".format(msg)

    @staticmethod
    def create_attack_order(position):
        return "TORPEDO {} {}".format(position.x, position.y)

    @classmethod
    def create_number_of_possible_position_order(cls, enemy_ship):
        return cls.create_msg_order(
            enemy_ship.number_of_possible_positions
        )


class ServiceTorpedo:
    @staticmethod
    def chose_torpedo(ship, enemy_ship):
        if ship.torpedo_cooldown > 0:
            return False
        within_range_positions = ServiceTorpedo.find_within_range_torpedo_positions(
            ship,
            enemy_ship
        )
        possible_attack_position = ServiceTorpedo. find_position_in_range_with_potential_enemy(
            within_range_positions,
            enemy_ship
        )
        if len(possible_attack_position) == 0:
            return False
        safe_attack_position = ServiceTorpedo.find_safest_attack_position(
            ship,
            possible_attack_position
        )
        return ServiceOrder.create_attack_order(safe_attack_position)

    @staticmethod
    def find_safest_attack_position(ship, positions):
        best_position = positions[0]
        best_distance = 0
        for position in positions:
            distance = position.get_distance(ship.position)
            if distance > best_distance:
                best_distance = distance
                best_position = position
        return best_position

    @staticmethod
    def find_within_range_torpedo_positions(ship, enemy_ship):
        possible_positions = []
        for x in range(enemy_ship.enemy_board.width):
            for y in range(enemy_ship.enemy_board.height):
                if ship.position.get_distance(Position(x, y)) <= 4:
                    possible_positions.append(Position(x, y))
        return possible_positions

    @staticmethod
    def find_position_in_range_with_potential_enemy(list_positions, enemy_ship):
        potential_positions = []
        for position in list_positions:
            if enemy_ship.enemy_board.get_cell(position).can_be_enemy_position:
                potential_positions.append(position)
        return potential_positions


#################
#################
##### Main ######
#################
#################
# Init
global_data, board, ennemy_ship, my_ship = ServiceUtils.init()

# game loop
while True:
    # read turn data and update own ship accordingly
    turn_data = ServiceUtils.read_turn_data()
    my_ship.update_turn_data(turn_data)

    # Read and analyse opponent order
    ennemy_ship.read_opponent_order(turn_data["opponent_orders"])

    move_order = ServiceMovement.chose_movement_and_move(my_ship, board)
    attack_order = ServiceTorpedo.chose_torpedo(my_ship, ennemy_ship)
    message_order = ServiceOrder.create_number_of_possible_position_order(ennemy_ship)
    if not move_order:
        move_order = ServiceMovement.surface(board)
    orders = ServiceOrder.concatenate_order([move_order, attack_order, message_order])
    ServiceOrder.display_order(orders)
