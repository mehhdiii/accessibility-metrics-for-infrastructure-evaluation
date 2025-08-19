from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.IRamp import AbstractRamp

class AbstractPlatform(ABC):
    """Abstract base class for Platform implementations."""
    
    def __init__(self, name: str, length: float, width: float):
        self.name = name
        self.length = length
        self.width = width
        self.parentRamp: "AbstractRamp | None" = None
        self.position: list[float] | None = None
    
    @property
    @abstractmethod
    def dimensions(self) -> tuple[float, float]:
        """Return the dimensions of the platform as a tuple (length, width)."""
        pass
    
    @property
    @abstractmethod
    def pose(self) -> tuple[float, float, float, float, float, float]:
        """Return the 6DOF pose as a tuple (x, y, z, roll, pitch, yaw)."""
        pass
    
    @abstractmethod
    def init(self, ramp: "AbstractRamp") -> None:
        """Initialize the platform with a parent ramp and calculate position."""
        pass
    
    @abstractmethod
    def render(self) -> str:
        """Render the platform as SDF XML string."""
        pass
    
    @abstractmethod
    def _calculate_position(self) -> list[float]:
        """Calculate platform position relative to parent ramp."""
        pass
    
    @abstractmethod
    def _buildAssetName(self) -> str:
        """Build the asset filename for this platform."""
        pass