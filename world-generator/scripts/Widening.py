import os
import uuid
from Wall import Wall
from Floor import Floor
from Corridor import Corridor

class Widening:
    def __init__(self, name: str, length: float, width: float, front_close: bool = False):
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
        self._floor: Floor | None = None
        self._leftTransitionWall: Wall | None = None
        self._rightTransitionWall: Wall | None = None

        self._frontClose: bool = front_close
        self._frontCloseWall: Wall | None = None

        self._previous_corridor: Corridor | None = None  # Reference to the previous corridor to which the widening is connected

    def init(self, y_index, x_index, previous_corridor: Corridor):
        self._previous_corridor = previous_corridor
        self.position = self._calculate_position(y_index, x_index)

        self.initializeWalls()
        self.initializeTransitionWalls()
        if (self._frontClose):
            self.initializeFrontCloseWall()
        self.initializeFloor()

    def _calculate_position(self, y_index, x_index):
        if (self._previous_corridor is None):
            raise ValueError("Widening is not connected to a corridor")
        # Calculate the position based on the indices
        if (self._previous_corridor.position is None):
            raise ValueError("Previous corridor position is not set.")
        
        x = self._previous_corridor.position[0] + (self._previous_corridor.length/2) + (self.length/2)  # calculation for x position
        y = self._previous_corridor.position[1]    # calculation for y position
        z = 0.0               # Fixed z position
        return [x, y, z]

    def initializeWalls(self):
        self._leftWall = Wall(f"{self.name}_left", length=self.length) 
        self._rightWall = Wall(f"{self.name}_right", length=self.length)

        if (self.position is None):
            raise ValueError("Widening position is not set.")

        #initialize the left wall to be W/2 from the center of widening
        self._leftWall.init([self.position[0], self.position[1] - (self.width / 2), self.position[2]])
        #initialize the right wall to be W/2 from the center of widening
        self._rightWall.init([self.position[0], self.position[1] + (self.width / 2), self.position[2]])

    def initializeTransitionWalls(self):

        if (self.position is None):
            raise ValueError("Widening position is not set.")
        
        if (self._previous_corridor is None):
            raise ValueError("No corridor connected to widening. cant initialize transition walls")

        transitionDelta = self.width/2 - self._previous_corridor.width/2
        transitionWidth = abs(transitionDelta)
        self._leftTransitionWall = Wall(f"{self.name}_left_transition", length=transitionWidth, yaw=1.57)
        self._rightTransitionWall = Wall(f"{self.name}_right_transition", length=transitionWidth, yaw=1.57)


        #initialize the left wall to be W/2 from the center of widening
        self._leftTransitionWall.init([self.position[0] - self.length/2, self.position[1] - (self.width / 2) + transitionDelta/2 , self.position[2]])
        #initialize the right wall to be W/2 from the center of widening
        self._rightTransitionWall.init([self.position[0] - self.length/2, self.position[1] + (self.width / 2) - transitionDelta/2, self.position[2]])

    def initializeFrontCloseWall(self):
        self._frontCloseWall = Wall(f"{self.name}_front_close", length=self.width, yaw=1.57)
        if (self.position is None):
            raise ValueError("Widening position is not set.")
        self._frontCloseWall.init([self.position[0] + self.length/2, self.position[1], self.position[2]])

    def initializeFloor(self):
        if (self.position is None):
            raise ValueError("Widening position is not set.")

        self._floor = Floor(f"{self.name}_floor", self.length, self.width)
        self._floor.init([self.position[0], self.position[1], self.position[2]])

    @property
    def asset_name(self):
        if (self._leftWall is None or self._rightWall is None):
            raise ValueError("Widening walls are not initialized.")

        return self._leftWall.asset_name + "," + self._rightWall.asset_name
    
    @property
    def dimensions(self):
        """Return the dimensions of the Widening as a tuple (length, height, thickness)."""
        return (self.length)

    @property
    def pose(self):
        if not self.position:
            raise ValueError("Widening position is not set.")
        if len(self.position) < 3:
            raise ValueError("Widening position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"Widening(length={self.length}, position={self.position})"

    def render(self):
        if self.position is None:
            raise ValueError("Widening position is not set. Please set the position before rendering.")
        if self._leftWall is None or self._rightWall is None:
            raise ValueError("Widening walls are not initialized.")
        if self._leftTransitionWall is None or self._rightTransitionWall is None:
            raise ValueError("Widening transition walls are not initialized.")
        if self._floor is None:
            raise ValueError("Widening floor is not initialized.")
        rendered = ''
        if (self._frontClose and self._frontCloseWall is not None):
            rendered = self._frontCloseWall.render()
        rendered += self._leftWall.render() + self._rightWall.render() + self._floor.render() + self._leftTransitionWall.render() + self._rightTransitionWall.render()
        return rendered