import os
import uuid

class StairCase:
    def __init__(self, name: str, numberOfSteps: int):
        self.name = name
        self.id = str(uuid.uuid4())
        self.numberOfSteps = numberOfSteps
        self.y_offset: float = float(os.getenv("Y_OFFSET", -1.0))
        self.x_offset: float = float(os.getenv("X_OFFSET", -1.0))

        if (self.y_offset == -1.0):
            raise ValueError("Y_OFFSET environment variable is not set.")
        if (self.x_offset == -1.0):
            raise ValueError("X_OFFSET environment variable is not set.")

    def init(self, yIndex: int, xIndex: int):

        self.position = self._calculate_position(yIndex, xIndex)
        self.initialize_stair()


    def _calculate_position(self, yIndex: int, xIndex: int):
        # Calculate the position based on the indices
        x =  xIndex * self.x_offset  # calculation for x position
        y = yIndex * self.y_offset    # calculation for y position
        z = 0.0               # Fixed z position
        return [x, y, z, 0, 0, 0]

    def initialize_stair(self):
        pass

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
        return f"StairCase(stepCount={self.numberOfSteps}, position={self.position})"

    def render(self):
        return ""