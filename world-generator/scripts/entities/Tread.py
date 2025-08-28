import os
import uuid
from entities.Riser import Riser

class Tread:
    def __init__(self, name: str, depth: float, width: float):
        self.name = name
        self.id = str(uuid.uuid4())
        self.depth = depth
        self.width = width  # Typical tread width
        self.thickness = 0.01  # Negligible tread thickness
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
        if not self.assets_url:
            raise ValueError("ASSETS_URL environment variable is not set.")
        self.asset_name = self._buildAssetName()
        self.previous_riser: Riser | None = None

    def _buildAssetName(self):
        return "tread_unit.stl"

    def init(self, position: list[float]):
        if len(position) != 3:
            raise ValueError("Tread position must have 3 elements [x, y, z].")
        self.position = position

    @property
    def dimensions(self):
        """Return the dimensions of the tread as a tuple (depth, width, thickness)."""
        return (self.depth, self.width, self.thickness)

    @property
    def pose(self):
        if not self.position:
            raise ValueError("Tread position is not set.")
        if len(self.position) < 3:
            raise ValueError("Tread position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"Tread(depth={self.depth}, width={self.width}, thickness={self.thickness}, position={self.position})"

    def render(self):
        if self.position is None:
            raise ValueError("Tread position is not set. Please set the position before rendering.")

        return f"""
        <model name="tread_{self.name}_{self.id}">
            <static>true</static>
            <pose>{" ".join(map(str, self.position))} 0 0 0</pose>
            <link name="link">
                <visual name="visual">
                <geometry>
                    <mesh>
                    <uri>{self.assets_url}/{self.asset_name}</uri>
                    <scale>{self.depth} {self.width} 1</scale> <!-- dont scale thickness -->
                    </mesh>
                </geometry>
                <material>
                    <ambient>0.3 0.3 0.3 1</ambient>
                    <diffuse>0.3 0.3 0.3 1</diffuse>
                </material>
                </visual>
                <collision name="collision">
                <geometry>
                        <box>
                            <size>{self.depth} {self.width} {self.thickness}</size> <!-- match final scaled size -->
                        </box>
                </geometry>
                </collision>
            </link>
        </model>
        """