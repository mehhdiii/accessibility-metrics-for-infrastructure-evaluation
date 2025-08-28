from entities.Ramp import Ramp 
class RampMapper:
    def __init__(self):
        pass


    @staticmethod
    def rampMapper(rampSpec):
        length = rampSpec.get("length")
        width = rampSpec.get("width")
        height = rampSpec.get("height")
        kerb_height = rampSpec.get("kerb_height")
        name = rampSpec.get("name")

        if length is None:
            raise ValueError("Missing 'length' in ramp item.")
        if width is None:
            raise ValueError("Missing 'width' in ramp item.")
        if height is None:
            raise ValueError("Missing 'height' in ramp item.")
        if kerb_height is None:
            raise ValueError("Missing 'kerb_height' in ramp item.")
        
        return Ramp(name, length, width, height, kerb_height)