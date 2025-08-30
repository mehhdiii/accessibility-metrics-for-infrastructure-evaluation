import os
import uuid
from entities.Riser import Riser 
from entities.Tread import Tread
class Stair:
    def __init__(self, name: str, width: float, depth: float, height: float):
        self.name = name
        self.id = str(uuid.uuid4())
        self.width = width
        self.depth = depth
        self.height = height
        self.riser: Riser = Riser(f"riser_{self.id}", self.height, self.width)
        self.tread: Tread = Tread(f"tread_{self.id}", self.depth, self.width)

    def init(self, position: list[float]):
        self.position = position
        self.riser.init(position)

        if (self.riser.position is None):
            raise ValueError("Riser position is not set.")
        
        tread_position = [self.riser.position[0]+self.tread.depth/2, self.riser.position[1], self.riser.position[2] + self.riser.height]
        self.tread.init(tread_position)

    @property
    def asset_name(self):
        return self.riser.asset_name + ', ' + self.tread.asset_name + ', '

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
        return self.riser.render() + self.tread.render()