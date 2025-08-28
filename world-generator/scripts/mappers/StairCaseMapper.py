

from entities.StairCase import StairCase

class StairCaseMapper:
    def __init__(self):
        pass

    @staticmethod
    def StairCaseMapper(stairCaseSpec):
        number_of_steps = stairCaseSpec.get("num_steps")
        width = stairCaseSpec.get("width")
        name = stairCaseSpec.get("name")
        riser_height = stairCaseSpec.get("riser_height")
        tread_depth = stairCaseSpec.get("tread_depth")

        if number_of_steps is None:
            raise ValueError("Missing 'num_steps' in stair case item.")
        if width is None:
            raise ValueError("Missing 'width' in stair case item.")
        if riser_height is None:
            raise ValueError("Missing 'riser_height' in stair case item.")
        if tread_depth is None:
            raise ValueError("Missing 'tread_depth' in stair case item.")

        return StairCase(name, number_of_steps, width, tread_depth, riser_height)