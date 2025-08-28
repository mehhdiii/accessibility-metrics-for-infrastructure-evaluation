import os
import uuid
from entities.Tread import Tread
from entities.Riser import Riser
from typing import TypedDict

# type used to store each step's tread and riser
class StepDict(TypedDict):
    tread: Tread
    riser: Riser

class StairCase:
    def __init__(self, name: str, numberOfSteps: int, width: float, tread_depth: float, riser_height: float):
        self.name = name
        self.id = str(uuid.uuid4())
        self.numberOfSteps = numberOfSteps
        self.width = width
        self.tread_depth = tread_depth
        self.riser_height = riser_height
        self.tread_riser_dict: list[StepDict] = []
        self.y_offset: float = float(os.getenv("Y_OFFSET", -1.0))
        self.x_offset: float = float(os.getenv("X_OFFSET", -1.0))

        if (self.y_offset == -1.0):
            raise ValueError("Y_OFFSET environment variable is not set.")
        if (self.x_offset == -1.0):
            raise ValueError("X_OFFSET environment variable is not set.")

    def init(self, yIndex: int, xIndex: int):

        self.position = self._calculate_position(yIndex, xIndex)
        self.initialize_stair()

    @property
    def asset_name(self):
        assetNames = ''
        for step in self.tread_riser_dict:
            assetNames += step['tread'].asset_name + ', ' + step['riser'].asset_name + ', '
        return assetNames

    def _calculate_position(self, yIndex: int, xIndex: int):
        # Calculate the position based on the indices
        x =  xIndex * self.x_offset  # calculation for x position
        y = yIndex * self.y_offset    # calculation for y position
        z = 0.0               # Fixed z position
        return [x, y, z, 0, 0, 0]

    def initialize_stair(self):
        if (self.numberOfSteps <= 0):
            raise ValueError("Number of steps must be greater than 0.")
        self.tread_riser_dict = [] # always clear before filling it up:
        last_riser = None
        for i in range(self.numberOfSteps):
            # Initialize each step's position and dimensions
            tread = Tread(f"tread_{self.id}_{i}", self.tread_depth, self.width)
            riser = Riser(f"riser_{self.id}_{i}", self.riser_height, self.width)

            tread_position = [self.position[0], self.position[1], self.position[2]]

            if (last_riser is not None):
                # i != 0 case:
                if (last_riser.position is None):
                    raise ValueError("Last riser position is not set.")
                tread_position = [last_riser.position[0] + self.tread_depth/2, last_riser.position[1], last_riser.position[2] + self.riser_height]   
            
            tread.init(tread_position)

            if (tread.position is None):
                raise ValueError("Tread position is not set.")
            riser_position = [tread.position[0] + self.tread_depth/2, tread.position[1], tread.position[2]]
            riser.init(riser_position)

            self.tread_riser_dict.append({"tread": tread, "riser": riser})
            last_riser = riser

    @property
    def dimensions(self):
        """Return the dimensions of the stair as a tuple (length, height, thickness)."""
        return (self.tread_depth, self.riser_height, self.width)

    @property
    def pose(self):
        if not self.position:
            raise ValueError("StairCase position is not set.")
        if len(self.position) < 3:
            raise ValueError("StairCase position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"StairCase(stepCount={self.numberOfSteps}, position={self.position})"

    def render(self):
        rendered = ""
        for step in self.tread_riser_dict:
            riser: Riser = step['riser']
            tread: Tread = step['tread']
            rendered += riser.render()
            rendered += tread.render()
        return rendered