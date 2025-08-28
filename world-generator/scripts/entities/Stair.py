import os
import uuid

class Stair:
    def __init__(self, name: str):
        self.name = name
        self.id = str(uuid.uuid4())

    def init(self, position: list[float]):
        self.position = position



    def _calculate_position(self, yIndex: int, xIndex: int):
        return [0, 0, 0, 0, 0, 0]

    @property
    def dimensions(self):
        """Return the dimensions of the stair as a tuple (length, height, thickness)."""
        raise ValueError('Not implemented')

    @property
    def pose(self):
        if not self.position:
            raise ValueError("StairCase position is not set.")
        if len(self.position) < 3:
            raise ValueError("StairCase position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"Stair(position={self.position})"

    def render(self):
        return ""