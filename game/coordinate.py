"""Координата"""


class Coordinate:
    """Координата"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return self.x + self.y * 10

    def is_coordinate_on_desk(self):
        """Проверить находится ли поле с
                        данной координатой на доске"""
        return 0 <= self.x <= 7 and 0 <= self.y <= 7
