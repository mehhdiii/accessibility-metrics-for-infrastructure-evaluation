from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if (TYPE_CHECKING):

    from interfaces.IPlatform import AbstractPlatform

class AbstractRamp(ABC):
    """Abstract base class for Ramp implementations."""
    
    def __init__(self, name: str, length: float, width: float, height: float, kerb_height: float):
        """
        Initialize a Ramp object.
        
        Args:
            name (str): Name identifier for the ramp
            length (float): Length of the ramp in meters
            width (float): Width of the ramp in meters  
            height (float): Height of the ramp in meters
            kerb_height (float): Height of the kerb in meters
        """
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.kerb_height = kerb_height
        self.position: Optional[list[float]] = None
        self.parentPlatform: "AbstractPlatform | None" = None

    @property
    @abstractmethod
    def dimensions(self) -> tuple[float, float, float]:
        """Return the dimensions of the ramp as a tuple (length, width, height)."""
        pass
    
    @property
    @abstractmethod
    def slope_percentage(self) -> float:
        """Calculate the slope percentage of the ramp."""
        pass
    
    @property
    @abstractmethod
    def is_valid_slope(self) -> bool:
        """Check if the ramp slope is within valid range (≤ 8%)."""
        pass
    
    @property
    @abstractmethod
    def is_wheelchair_accessible(self) -> bool:
        """Check if ramp width is sufficient for wheelchair access (≥ 0.9m)."""
        pass
    
    @abstractmethod
    def init(self, index: int) -> None:
        """Initialize the ramp with an index and calculate position."""
        pass
    
    @abstractmethod
    def buildAssetName(self) -> str:
        """Build the asset filename for this ramp."""
        pass
    
    @abstractmethod
    def _calculate_position(self) -> list[float]:
        """Calculate ramp position based on index and parent platform."""
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the Ramp instance to a dictionary."""
        pass
    
    @abstractmethod
    def render(self) -> str:
        """Render the ramp as SDF XML string."""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """Return human-readable string representation."""
        pass
    
    @abstractmethod
    def __repr__(self) -> str:
        """Return developer-friendly string representation."""
        pass