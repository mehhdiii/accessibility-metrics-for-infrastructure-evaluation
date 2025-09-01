import os
import uuid
from entities.Ramp import Ramp  # Remove this import if Ramp is not used elsewhere
from entities.Wall import Wall  # Changed from Kerb to Wall
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.StairCase import StairCase  # Make sure this import is correct

class Landing:
    def __init__(self, name: str, length: float, width: float, front_wall: bool = False, walled: bool = False):
        self.name = name
        self.id = str(uuid.uuid4())
        self.length = length
        self.width = width
        self.front_wall = front_wall
        self.walled = walled
        self.thickness = 0.01 #default thickness 
        self.parentStairCase: StairCase | None = None
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
        self._leftTransitionStartWall: Wall | None = None
        self._rightTransitionStartWall: Wall | None = None
        self._leftTransitionEndWall: Wall | None = None
        self._rightTransitionEndWall: Wall | None = None
        self.front_close_wall: Wall | None = None
        self._leftWall: Wall | None = None
        self._rightWall: Wall | None = None
        if not self.assets_url:
            raise ValueError("ASSETS_URL environment variable is not set.")
        self.asset_name = self._buildAssetName()

    def _buildAssetName(self):
        return f"platform_unit.stl"
    
    
    def init(self, position: list[float], corridor):
        self.parentStairCase = corridor
        self.position = position
        print('landing position set:', self.position)
        if self.isTransitionWallRequired():
            self.initializeTransitionWalls()
        if (self.walled):
            self.initializeWalls()
        if self.front_wall:
            self.initializeFrontCloseWall()

    def initializeWalls(self):
        if self.parentStairCase is None:
            raise ValueError("No parent corridor connected to platform.")
        
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
        
        if (self.parentStairCase is None):
            raise ValueError("No corridor connected to widening. cant initialize transition walls")

        transitionDelta = self.width/2 - self.parentStairCase.width/2
        transitionWidth = abs(transitionDelta)
        self._leftTransitionStartWall = Wall(f"{self.name}_left_transition", length=transitionWidth, height= self.parentStairCase.wall_height, yaw=1.57)
        self._rightTransitionStartWall = Wall(f"{self.name}_right_transition", length=transitionWidth, height= self.parentStairCase.wall_height, yaw=1.57)
        #initialize the left wall to be W/2 from the center of widening
        self._leftTransitionStartWall.init([self.position[0] - self.length/2, self.position[1] - (self.width / 2) + transitionDelta/2 , self.position[2]])
        #initialize the right wall to be W/2 from the center of widening
        self._rightTransitionStartWall.init([self.position[0] - self.length/2, self.position[1] + (self.width / 2) - transitionDelta/2, self.position[2]])


        if (not self.front_wall):

            self._leftTransitionEndWall = Wall(f"{self.name}_left_transition_end", length=transitionWidth, yaw=1.57)
            self._rightTransitionEndWall = Wall(f"{self.name}_right_transition_end", length=transitionWidth, yaw=1.57)

            self._leftTransitionEndWall.init([self.position[0] + self.length/2, self.position[1] - (self.width / 2) + transitionDelta/2, self.position[2]])
            self._rightTransitionEndWall.init([self.position[0] + self.length/2, self.position[1] + (self.width / 2) - transitionDelta/2, self.position[2]])

    def initializeFrontCloseWall(self):
        if self.parentStairCase is None:
            raise ValueError("No parent corridor connected to platform.")
        if self.position is None:
            raise ValueError("Platform position is not set.")
        self.front_close_wall = Wall(f"{self.name}_front_close", length=self.width, yaw=1.57)
        self.front_close_wall.init([self.position[0] + self.length/2, self.position[1], self.position[2]])
    def isTransitionWallRequired(self):
        if not self.parentStairCase:
            raise ValueError("Parent corridor is not set.")
        return self.width != self.parentStairCase.width

    @property
    def dimensions(self):
        """Return the dimensions of the platform as a tuple (length, width)."""
        return (self.length, self.width)
    @property
    def pose(self):
        if not self.position:
            raise ValueError("Platform position is not set.")
        if (len(self.position) < 6):
            raise ValueError("Platform position must have at least 6 elements.")
        return self.position[0], self.position[1], self.position[2], self.position[3], self.position[4], self.position[5]

    def _calculate_position(self):
        if not self.parentStairCase:
            raise ValueError("Parent corridor is not set.")
        
        corridor_position = self.parentStairCase.position
        if (corridor_position is None or len(corridor_position) < 3):
            raise ValueError("Parent corridor position is not set.")

        x = corridor_position[0] + self.length/2 + self.parentStairCase.length/2

        y = corridor_position[1] # copy y coordinate of the corridor
        z = corridor_position[2] + self.parentStairCase.height
        return [x, y, z, 0, 0, 0]

    def __repr__(self):
        return f"Platform(length={self.length}, width={self.width}, position={self.position})"
    
    def render(self):
        if self.position is None:
            raise ValueError("Platform position is not set. Please set the position before rendering.")
        rendered = ''
        if self._leftTransitionStartWall is not None and self._rightTransitionStartWall is not None:
            rendered += self._leftTransitionStartWall.render() + self._rightTransitionStartWall.render()
        if self._leftTransitionEndWall is not None and self._rightTransitionEndWall is not None:
            rendered += self._leftTransitionEndWall.render() + self._rightTransitionEndWall.render()
        if self.front_close_wall:
            rendered += self.front_close_wall.render()
        rendered += self._leftWall.render() if self._leftWall is not None else ''
        rendered += self._rightWall.render() if self._rightWall is not None else ''

        rendered += f"""
        <model name="platform_{self.name}_{self.id}">
            <static>true</static>
            <pose>{" ".join(map(str, self.position))} 0 0 0</pose>
            <link name="link">
                <visual name="visual">
                <geometry>
                    <mesh>
                    <uri>{self.assets_url}/{self.asset_name}</uri>
                    <scale>{self.length} {self.width} 1</scale> <!-- dont scale height, thickness -->
                    </mesh>
                </geometry>
                </visual>
                <collision name="collision">
                <geometry>
                        <box>
                            <size>{self.length} {self.width} {self.thickness}</size> <!-- match final scaled size -->
                        </box>
                </geometry>
                </collision>
            </link>
        </model>
        """
        return rendered
