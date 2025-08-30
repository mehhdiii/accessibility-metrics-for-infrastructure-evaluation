import os
import uuid

class TactileStrip:
    def __init__(self, name: str, length: float, width: float):
        self.name = name
        self.id = str(uuid.uuid4())
        self.length = length
        self.width = width
        self.thickness = 0.02  # tactile strip thickness
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
        if not self.assets_url:
            raise ValueError("ASSETS_URL environment variable is not set.")
        self.asset_name = self._buildAssetName()

    def _buildAssetName(self):
        # Asset name can depend on pattern
        return f"tactile_strip_unit.stl"

    def init(self, position: list[float]):
        if len(position) != 3:
            raise ValueError("TactileStrip position must have 3 elements [x, y, z].")
        self.position = position

    @property
    def dimensions(self):
        """Return the dimensions of the tactile strip as a tuple (length, width, thickness)."""
        return (self.length, self.width, self.thickness)

    @property
    def pose(self):
        if not self.position:
            raise ValueError("TactileStrip position is not set.")
        if len(self.position) < 3:
            raise ValueError("TactileStrip position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"TactileStrip(length={self.length}, width={self.width}, thickness={self.thickness}, pattern={self.pattern}, position={self.position})"

    def render(self):
        if self.position is None:
            raise ValueError("TactileStrip position is not set. Please set the position before rendering.")

        return f"""
        <model name="tactile_strip_{self.name}_{self.id}">
            <static>true</static>
            <pose>{" ".join(map(str, self.position))} 0 0 0</pose>
            <link name="link">
                <visual name="visual">
                <geometry>
                    <mesh>
                    <uri>{self.assets_url}/{self.asset_name}</uri>
                    <scale>{self.length} {self.width} 1</scale>
                    </mesh>
                </geometry>
                <material>
                    <ambient>0.8 0.8 0.2 1</ambient>
                    <diffuse>0.8 0.8 0.2 1</diffuse>
                </material>
                </visual>
                <collision name="collision">
                <geometry>
                        <box>
                            <size>{self.length} {self.width} {self.thickness}</size>
                        </box>
                </geometry>
                </collision>
            </link>
        </model>
        """