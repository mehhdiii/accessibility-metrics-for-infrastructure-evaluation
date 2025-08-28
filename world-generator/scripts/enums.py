from enum import Enum

class ElementType(Enum):
    RAMP = "ramp"
    PLATFORM = "platform"
    CORRIDOR = "corridor"
    WIDENING = "widening"
    STAIRCASE = "staircase"

class SpecClassification(Enum):
    VALID = "valid"
    INVALID = "invalid"

