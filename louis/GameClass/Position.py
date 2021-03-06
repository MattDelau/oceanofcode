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
