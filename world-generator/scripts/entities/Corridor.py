import os
import uuid
from entities.Wall import Wall
from entities.Floor import Floor
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
        self._floor: Floor | None = None

        self._leftTransitionWall: Wall | None = None
        self._rightTransitionWall: Wall | None = None

        self._previous_widening = None  # Reference to the previous Widening to which the Corridor is connected

    def init(self, y_index, x_index):
        self.position = self._calculate_position(y_index, x_index)
        self.initializeWalls()
        if (self._previous_widening is not None):
            self.initializeTransitionWalls()
        self.initializeFloor()

    def _calculate_position(self, y_index, x_index):
        # Calculate the position based on the indices
        x =  x_index * self.x_offset  # calculation for x position
        y = y_index * self.y_offset    # calculation for y position
        z = 0.0               # Fixed z position
        if self._previous_widening is not None:
            px, py, pz = self._previous_widening.pose
            x = self.length / 2 + self._previous_widening.length / 2 + abs(px)
            z = pz     
        
        return [x, y, z]

    def initializeWalls(self):
        #use fixed thickness and height in the wall:

        self._leftWall = Wall(f"{self.name}_left", length=self.length) 
        self._rightWall = Wall(f"{self.name}_right", length=self.length)

        if (self.position is None):
            raise ValueError("Corridor position is not set.")
        
        #initialize the left wall to be W/2 from the center of corridor
        self._leftWall.init([self.position[0], self.position[1] - (self.width / 2), self.position[2]])
        #initialize the right wall to be W/2 from the center of corridor
        self._rightWall.init([self.position[0], self.position[1] + (self.width / 2), self.position[2]])

    def initializeTransitionWalls(self):

        if (self.position is None):
            raise ValueError("Widening position is not set.")
        
        if (self._previous_widening is None):
            raise ValueError("No corridor connected to widening. cant initialize transition walls")

        transitionDelta = self.width/2 - self._previous_widening.width/2
        transitionWidth = abs(transitionDelta)
        self._leftTransitionWall = Wall(f"{self.name}_left_transition", length=transitionWidth, yaw=1.57)
        self._rightTransitionWall = Wall(f"{self.name}_right_transition", length=transitionWidth, yaw=1.57)


        #initialize the left wall to be W/2 from the center of widening
        self._leftTransitionWall.init([self.position[0] - self.length/2, self.position[1] - (self.width / 2) + transitionDelta/2 , self.position[2]])
        #initialize the right wall to be W/2 from the center of widening
        self._rightTransitionWall.init([self.position[0] - self.length/2, self.position[1] + (self.width / 2) - transitionDelta/2, self.position[2]])

    def initializeFloor(self):
        if (self.position is None):
            raise ValueError("Corridor position is not set.")

        self._floor = Floor(f"{self.name}_floor", self.length, self.width)
        self._floor.init([self.position[0], self.position[1], self.position[2]])

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
        if self._floor is None:
            raise ValueError("Corridor floor is not initialized.")
        if (self._leftTransitionWall is None or self._rightTransitionWall is None) and self._previous_widening is not None:
            raise ValueError("Corridor transition walls are not initialized while we have a preceeding Widening.")

        rendered =  self._leftWall.render() + self._rightWall.render() + self._floor.render()

        if (self._leftTransitionWall is not None and self._rightTransitionWall is not None):
            rendered += self._leftTransitionWall.render() + self._rightTransitionWall.render()
        return rendered