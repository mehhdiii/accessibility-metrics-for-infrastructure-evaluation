import os
import uuid
from Ramp import Ramp

class Platform:
    def __init__(self, name: str, length: float, width: float):
        self.name = name
        self.id = str(uuid.uuid4())
        self.length = length
        self.width = width
        self.parentRamp: Ramp | None = None
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
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

    @property
    def dimensions(self):
        """Return the dimensions of the platform as a tuple (length, width)."""
        return (self.length, self.width)

    def _calculate_position(self):
        if not self.parentRamp:
            raise ValueError("Parent ramp is not set.")
        
        ramp_position = self.parentRamp.position
        if (ramp_position is None or len(ramp_position) < 3):
            raise ValueError("Parent ramp position is not set.")

        x = self.length/2 + self.parentRamp.length/2
        #invert x:
        x = -x

        y = ramp_position[1] # copy y coordinate of the ramp
        z = self.parentRamp.height
        return [x, y, z, 0, 0, 0]

    def __repr__(self):
        return f"Platform(length={self.length}, width={self.width}, position={self.position})"
    
    def render(self):
        if self.position is None:
            raise ValueError("Platform position is not set. Please set the position before rendering.")

        return f"""
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



