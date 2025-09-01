import math
import os
import uuid
from interfaces.IPlatform import AbstractPlatform
from entities.Kerb import Kerb

class Ramp():
    def __init__(self, name: str, length: float, width: float, height: float, kerb_height: float):
        """
        Initialize a Ramp object.
        
        Args:
            length (float): Length of the ramp in meters
            width (float): Width of the ramp in meters  
            height (float): Height of the ramp in meters
            kerb_height (float): Height of the kerb in meters
            position (float.array(6)): Position along the path (default: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        """
        self.name = name
        self.id = str(uuid.uuid4())  # Generate unique UUID
        self.y_offset: float = float(os.getenv("Y_OFFSET", 2.0))

        self.length = length
        self.width = width
        self.height = height
        self.kerb_height = kerb_height
        self.parentPlatform: AbstractPlatform | None = None
        self.kerb_left: Kerb = Kerb(self.name, self.ramp_hypotenuse, self.kerb_height, pitch=-self.calculate_slope_angle)
        self.kerb_right: Kerb = Kerb(self.name, self.ramp_hypotenuse, self.kerb_height, pitch=-self.calculate_slope_angle)
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
        if not self.assets_url:
            raise ValueError("ASSETS_URL environment variable is not set.")
        self.asset_name = self.buildAssetName()

    @property
    def ramp_hypotenuse(self):
        return math.hypot(self.length, self.height)

    def buildAssetName(self):
        l = self.length
        w = self.width
        h = self.height
        if (self.length == int(self.length)):
            l = int(self.length)
        if (self.width == int(self.width)):
            w = int(self.width)
        if (self.height == int(self.height)):
            h = int(self.height)
        return f"ramp_{l}_{w}_{h}.stl"

    def init(self, index): 
        self.index = index
        self.position = self._calculate_position()
        self.initialize_kerb()

    def initialize_kerb(self):
        if self.position is None:
            raise ValueError("Ramp position is not set. Please set the position before initializing the kerb.")
        self.kerb_left.init([self.position[0], self.position[1] - (self.width / 2), self.position[2] + self.height/2])
        self.kerb_right.init([self.position[0], self.position[1] + (self.width / 2), self.position[2] + self.height/2])

    def _calculate_position(self):
        y = self.index * self.y_offset
        x = 0
        z = 0
        if (self.parentPlatform):
            px, py, pz, _, _, _ = self.parentPlatform.pose
            x = self.length / 2 + self.parentPlatform.length / 2 + abs(px)
            z = pz

        return [x, y, z, 0, 0, 0]

    @property
    def dimensions(self):
        """Return the dimensions of the ramp as a tuple (length, width, height)."""
        return (self.length, self.width, self.height)

    @property
    def slope_percentage(self):
        """Calculate the slope percentage of the ramp."""
        if self.length == 0:
            return 0
        return (self.height / self.length) * 100
    
    @property
    def calculate_slope_angle(self):
        return math.atan(self.height / self.length)

    @property
    def is_valid_slope(self):
        """Check if the ramp slope is within valid range (≤ 8%)."""
        return self.slope_percentage <= 8.0
    
    @property
    def is_wheelchair_accessible(self):
        """Check if ramp width is sufficient for wheelchair access (≥ 0.9m)."""
        return self.width >= 0.9
    
    def __str__(self):
        return (f"Ramp(length={self.length}m, width={self.width}m, "
                f"height={self.height}m, kerb={self.kerb_height}m, "
                f"position={self.position}m, slope={self.slope_percentage:.1f}%)")
    
    def __repr__(self):
        return (f"Ramp({self.length}, {self.width}, {self.height}, "
                f"{self.kerb_height}, {self.position})")
    
    def to_dict(self):
        """Convert the Ramp instance to a dictionary."""
        return {
            "length": self.length,
            "width": self.width,
            "height": self.height,
            "kerb_height": self.kerb_height,
            "position": self.position
        }
    
    def render(self):
        if self.position is None:
            raise ValueError("Ramp position is not set. Please set the position before rendering.")
        rendered = self.kerb_left.render() + self.kerb_right.render()
        
        
        rendered += f"""
        <model name="ramp_{self.name}_{self.id}">
            <static>true</static>
            <pose>{" ".join(map(str, self.position))}</pose>
            <link name="link">
        <visual name="visual">
            <geometry>
            <mesh>
                <uri>{self.assets_url}/{self.asset_name}</uri>
            </mesh>
            </geometry>
            <material>
                <ambient>0.6 0.4 0.2 1</ambient>
                <diffuse>0.6 0.4 0.2 1</diffuse>

            </material>
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
