from enum import Enum

class ElementType(Enum):
    RAMP = "ramp"
    PLATFORM = "platform"

class RampClassification(Enum):
    VALID = "valid"
    INVALID = "invalid"