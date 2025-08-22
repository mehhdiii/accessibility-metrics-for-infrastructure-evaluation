from enum import Enum

class ElementType(Enum):
    RAMP = "ramp"
    PLATFORM = "platform"
    CORRIDOR = "corridor"

class SpecClassification(Enum):
    VALID = "valid"
    INVALID = "invalid"

