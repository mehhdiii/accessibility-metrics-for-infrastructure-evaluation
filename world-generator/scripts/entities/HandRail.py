import os
import uuid

class HandRail:
    def __init__(self, name: str, length: float, height: float):
        self.name = name
        self.id = str(uuid.uuid4())
        self.length = length
        self.height = height
        self.diameter = 0.25
        self.position: list[float] | None = None
        self.assets_url = os.getenv("ASSETS_BASE_URL", None)
        if not self.assets_url:
            raise ValueError("ASSETS_URL environment variable is not set.")
        self.asset_name = self._buildAssetName()

    def _buildAssetName(self):
        return "handrail_unit.stl"

    def init(self, position: list[float]):
        if len(position) != 6:
            raise ValueError("HandRail position must have 6 elements [x, y, z, roll, pitch, yaw].")
        self.position = position
        self.position[2] += self.height  # Adjust z to be at half the height

    @property
    def dimensions(self):
        """Return the dimensions of the handrail as a tuple (length, height, diameter)."""
        return (self.length, self.height, self.diameter)

    @property
    def pose(self):
        if not self.position:
            raise ValueError("HandRail position is not set.")
        if len(self.position) < 3:
            raise ValueError("HandRail position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"HandRail(length={self.length}, height={self.height}, diameter={self.diameter}, position={self.position})"

    def render(self):
        if self.position is None:
            raise ValueError("HandRail position is not set. Please set the position before rendering.")

        return f"""
        <model name="handrail_{self.name}_{self.id}">
            <static>true</static>
            <pose>{" ".join(map(str, self.position))}</pose>
            <link name="link">
                <visual name="visual">
                <geometry>
                    <mesh>
                    <uri>{self.assets_url}/{self.asset_name}</uri>
                    <scale>{self.length} {self.diameter} {self.height}</scale>
                    </mesh>
                </geometry>
                <material>
                    <ambient>0.7 0.7 0.7 1</ambient>
                    <diffuse>0.7 0.7 0.7 1</diffuse>
                </material>
                </visual>
                <collision name="collision">
                <geometry>
                        <cylinder>
                            <radius>{self.diameter / 2}</radius>
                            <length>{self.length}</length>
                        </cylinder>
                </geometry>
                </collision>
            </link>
        </model>
        """
