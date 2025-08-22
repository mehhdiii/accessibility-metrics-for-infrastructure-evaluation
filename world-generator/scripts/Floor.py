import os
import uuid

class Floor:
    def __init__(self, name: str, length: float, height: float, thickness: float):
        self.name = name
        self.id = str(uuid.uuid4())
        self.length = length
        self.height = height
        self.thickness = thickness
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
        if not self.assets_url:
            raise ValueError("ASSETS_URL environment variable is not set.")
        self.asset_name = self._buildAssetName()

    def _buildAssetName(self):
        return f"floor_unit.stl"

    def init(self, position: list[float]):
        if len(position) != 3:
            raise ValueError("Floor position must have 3 elements [x, y, z].")
        self.position = position

    @property
    def dimensions(self):
        """Return the dimensions of the floor as a tuple (length, height, thickness)."""
        return (self.length, self.height, self.thickness)

    @property
    def pose(self):
        if not self.position:
            raise ValueError("Floor position is not set.")
        if len(self.position) < 3:
            raise ValueError("Floor position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"Floor(length={self.length}, height={self.height}, thickness={self.thickness}, position={self.position})"

    def render(self):
        if self.position is None:
            raise ValueError("Floor position is not set. Please set the position before rendering.")

        return f"""
        <model name="floor_{self.name}_{self.id}">
            <static>true</static>
            <pose>{" ".join(map(str, self.position))} 0 0 0</pose>
            <link name="link">
                <visual name="visual">
                <geometry>
                    <mesh>
                    <uri>{self.assets_url}/{self.asset_name}</uri>
                    <scale>{self.length} 1 1</scale> <!-- dont scale height, thickness -->
                    </mesh>
                </geometry>
                <material>
                    <ambient>0.6 0.4 0.2 1</ambient>
                    <diffuse>0.6 0.4 0.2 1</diffuse>
                </material>
                </visual>
                <collision name="collision">
                <geometry>
                        <box>
                            <size>{self.length} {self.thickness} {self.height}</size> <!-- match final scaled size -->
                        </box>
                </geometry>
                </collision>
            </link>
        </model>
        """