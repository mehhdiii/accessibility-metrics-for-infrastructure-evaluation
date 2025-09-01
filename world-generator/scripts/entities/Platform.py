import os
import uuid
from entities.Ramp import Ramp
from entities.Kerb import Kerb
from interfaces.IPlatform import AbstractPlatform
class Platform(AbstractPlatform):
    def __init__(self, name: str, length: float, width: float):
        self.name = name
        self.id = str(uuid.uuid4())
        self.length = length
        self.width = width
        self.parentRamp: Ramp | None = None
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
        self._leftTransitionStartKerb: Kerb | None = None
        self._rightTransitionStartKerb: Kerb | None = None
        self._leftTransitionEndKerb: Kerb | None = None
        self._rightTransitionEndKerb: Kerb | None = None

        self._leftKerb: Kerb | None = None
        self._rightKerb: Kerb | None = None
        if not self.assets_url:
            raise ValueError("ASSETS_URL environment variable is not set.")
        self.asset_name = self._buildAssetName()

    def _buildAssetName(self):
        l = self.length
        if (self.length == int(self.length)):
            l = int(self.length)
        w = self.width
        if (self.width == int(self.width)):
            w = int(self.width)
        return f"platform_{l}_{w}.stl"
    
    
    def init(self, ramp: Ramp):
        self.parentRamp = ramp
        self.position = self._calculate_position()
        if self.isTransitionKerbRequired():
            self.initializeTransitionKerbs()
        self.initializeKerbs()
    
    def initializeKerbs(self):
        if self.parentRamp is None:
            raise ValueError("No parent ramp connected to platform.")
        
        self._leftKerb = Kerb(f"{self.name}_left", length=self.length, height=self.parentRamp.kerb_height)
        self._rightKerb = Kerb(f"{self.name}_right", length=self.length, height=self.parentRamp.kerb_height)

        if (self.position is None):
            raise ValueError("Corridor position is not set.")

        #initialize the left kerb to be W/2 from the center of corridor
        self._leftKerb.init([self.position[0], self.position[1] - (self.width / 2), self.position[2]])
        #initialize the right kerb to be W/2 from the center of corridor
        self._rightKerb.init([self.position[0], self.position[1] + (self.width / 2), self.position[2]])


    def initializeTransitionKerbs(self):

        if (self.position is None):
            raise ValueError("Widening position is not set.")
        
        if (self.parentRamp is None):
            raise ValueError("No corridor connected to widening. cant initialize transition walls")

        transitionDelta = self.width/2 - self.parentRamp.width/2
        transitionWidth = abs(transitionDelta)
        self._leftTransitionStartKerb = Kerb(f"{self.name}_left_transition", length=transitionWidth, height= self.parentRamp.kerb_height, yaw=1.57)
        self._rightTransitionStartKerb = Kerb(f"{self.name}_right_transition", length=transitionWidth, height= self.parentRamp.kerb_height, yaw=1.57)

        self._leftTransitionEndKerb = Kerb(f"{self.name}_left_transition_end", length=transitionWidth, height= self.parentRamp.kerb_height, yaw=1.57)
        self._rightTransitionEndKerb = Kerb(f"{self.name}_right_transition_end", length=transitionWidth, height= self.parentRamp.kerb_height, yaw=1.57)

        #initialize the left wall to be W/2 from the center of widening
        self._leftTransitionStartKerb.init([self.position[0] - self.length/2, self.position[1] - (self.width / 2) + transitionDelta/2 , self.position[2]])
        #initialize the right wall to be W/2 from the center of widening
        self._rightTransitionStartKerb.init([self.position[0] - self.length/2, self.position[1] + (self.width / 2) - transitionDelta/2, self.position[2]])

        self._leftTransitionEndKerb.init([self.position[0] + self.length/2, self.position[1] - (self.width / 2) + transitionDelta/2, self.position[2]])
        self._rightTransitionEndKerb.init([self.position[0] + self.length/2, self.position[1] + (self.width / 2) - transitionDelta/2, self.position[2]])

    def isTransitionKerbRequired(self):
        if not self.parentRamp:
            raise ValueError("Parent ramp is not set.")
        return self.width != self.parentRamp.width

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
        if not self.parentRamp:
            raise ValueError("Parent ramp is not set.")
        
        ramp_position = self.parentRamp.position
        if (ramp_position is None or len(ramp_position) < 3):
            raise ValueError("Parent ramp position is not set.")

        x = ramp_position[0] + self.length/2 + self.parentRamp.length/2

        y = ramp_position[1] # copy y coordinate of the ramp
        z = ramp_position[2] + self.parentRamp.height
        return [x, y, z, 0, 0, 0]

    def __repr__(self):
        return f"Platform(length={self.length}, width={self.width}, position={self.position})"
    
    def render(self):
        if self.position is None:
            raise ValueError("Platform position is not set. Please set the position before rendering.")
        rendered = ''
        if self._leftTransitionStartKerb is not None and self._rightTransitionStartKerb is not None and self._leftTransitionEndKerb is not None and self._rightTransitionEndKerb is not None:
            rendered += self._leftTransitionStartKerb.render() + self._rightTransitionStartKerb.render()
            rendered += self._leftTransitionEndKerb.render() + self._rightTransitionEndKerb.render()
        rendered += self._leftKerb.render() if self._leftKerb is not None else ''
        rendered += self._rightKerb.render() if self._rightKerb is not None else ''

        rendered += f"""
        <model name="platform_{self.name}_{self.id}">
            <static>true</static>
            <pose>{" ".join(map(str, self.position))}</pose>
            <link name="link">
                <visual name="visual">
                <geometry>
                    <mesh>
                    <uri>{self.assets_url}/{self.asset_name}</uri>
                    </mesh>
                </geometry>
                </visual>
                <collision name="collision">
                <geometry>
                    <mesh>
                    <uri>{self.assets_url}/{self.asset_name}</uri>
                    </mesh>
                </geometry>
                </collision>
            </link>
        </model>
        """
        return rendered



