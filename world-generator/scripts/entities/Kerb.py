import os
import uuid

class Kerb:
    def __init__(self, name: str, length: float, height: float, yaw: float = 0.0, pitch: float = 0.0):
        self.name = name
        self.id = str(uuid.uuid4())
        self.length = length
        self.height = height  # Typical kerb height
        self.thickness = 0.1  # Typical kerb thickness
        self.yaw = yaw  # in radians
        self.pitch = pitch  # in radians
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
        if not self.assets_url:
            raise ValueError("ASSETS_URL environment variable is not set.")
        self.asset_name = self._buildAssetName()

    def _buildAssetName(self):
        return f"kerb_unit.stl"

    def init(self, position: list[float]):
        if len(position) != 3:
            raise ValueError("Kerb position must have 3 elements [x, y, z].")
        self.position = position

    @property
    def dimensions(self):
        """Return the dimensions of the kerb as a tuple (length, height, thickness)."""
        return (self.length, self.height, self.thickness)

    @property
    def pose(self):
        if not self.position:
            raise ValueError("Kerb position is not set.")
        if len(self.position) < 3:
            raise ValueError("Kerb position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"Kerb(length={self.length}, height={self.height}, thickness={self.thickness}, position={self.position})"

    def render(self):
        if self.position is None:
            raise ValueError("Kerb position is not set. Please set the position before rendering.")

        return f"""
        <model name="kerb_{self.name}_{self.id}">
            <static>true</static>
            <pose>{" ".join(map(str, self.position))} 0 {self.pitch} {self.yaw}</pose>
            <link name="link">
                <visual name="visual">
                <geometry>
                    <mesh>
                    <uri>{self.assets_url}/{self.asset_name}</uri>
                    <scale>{self.length} 1 {self.height}</scale>
                    </mesh>
                </geometry>
                <material>
                    <ambient>0.7 0.7 0.7 1</ambient>
                    <diffuse>0.7 0.7 0.7 1</diffuse>
                </material>
                </visual>
                <collision name="collision">
                <geometry>
                        <box>
                            <size>{self.length} {self.thickness} {self.height}</size>
                        </box>
                </geometry>
                </collision>
            </link>
        </model>
        """