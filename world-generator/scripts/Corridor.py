import os
import uuid
from Wall import Wall

class Corridor:
    def __init__(self, name: str, length: float, width: float):
        self.name = name
        self.id = str(uuid.uuid4())
        self.length = length
        self.width = width
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
        self.y_offset: float = float(os.getenv("Y_OFFSET", 2.0))
        self.x_offset: float = float(os.getenv("X_OFFSET", 25.0))

        self._leftWall: Wall | None = None
        self._rightWall: Wall | None = None

    def init(self, y_index, x_index):
        self.position = self._calculate_position(y_index, x_index)
        self.initializeWalls()

    def _calculate_position(self, y_index, x_index):
        # Calculate the position based on the indices
        x = x_index * self.x_offset  # calculation for x position
        y = y_index * self.y_offset    # calculation for y position
        z = 0.0               # Fixed z position
        return [x, y, z]

    def initializeWalls(self):
        #use fixed thickness and height in the wall:

        self._leftWall = Wall(f"{self.name}_left", self.length, 1.2, 0.1) 
        self._rightWall = Wall(f"{self.name}_right", self.length, 1.2, 0.1)
        
        if (self.position is None):
            raise ValueError("Corridor position is not set.")
        
        #initialize the left wall to be W/2 from the center of corridor
        self._leftWall.init([self.position[0], self.position[1] - (self.width / 2), self.position[2]])
        #initialize the right wall to be W/2 from the center of corridor
        self._rightWall.init([self.position[0], self.position[1] + (self.width / 2), self.position[2]])



    @property
    def asset_name(self):
        if (self._leftWall is None or self._rightWall is None):
            raise ValueError("Corridor walls are not initialized.")
        
        return self._leftWall.asset_name + "," + self._rightWall.asset_name
    
    @property
    def dimensions(self):
        """Return the dimensions of the Corridor as a tuple (length, height, thickness)."""
        return (self.length)

    @property
    def pose(self):
        if not self.position:
            raise ValueError("Corridor position is not set.")
        if len(self.position) < 3:
            raise ValueError("Corridor position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"Corridor(length={self.length}, position={self.position})"

    def render(self):
        if self.position is None:
            raise ValueError("Corridor position is not set. Please set the position before rendering.")
        if self._leftWall is None or self._rightWall is None:
            raise ValueError("Corridor walls are not initialized.")
        
        return self._leftWall.render() + self._rightWall.render()