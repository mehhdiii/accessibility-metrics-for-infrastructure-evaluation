

from entities.StairCase import StairCase
from entities.shared import HandrailSpecs
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
        tactile_strips = stairCaseSpec.get("tactile_strips")
        tactile_strip_attached = False
        tactile_strip_before_stairs_distance = 0.0
        tactile_strip_after_stairs_distance = 0.0
        if (tactile_strips):
            tactile_strip_before_stairs_distance = tactile_strips.get("before_length")
            tactile_strip_after_stairs_distance = tactile_strips.get("after_length")
            tactile_strip_attached = True
            if (tactile_strip_after_stairs_distance is None or tactile_strip_before_stairs_distance is None):
                raise ValueError("Missing tactile strip lengths in stair case item.")

        handrails = stairCaseSpec.get("handrails")
        extension_length = 0.0
        handRails: list[HandrailSpecs] = []
        if (handrails):
            for i in handrails:

                extension_length = i.get("extension_length")
                handrail_height = i.get("height")
                offset_from_wall = i.get("offset_from_wall")
                if (extension_length is None or handrail_height is None or offset_from_wall is None):
                    raise ValueError("Missing handrail lengths in stair case item.")
                handRails.append(HandrailSpecs(height=handrail_height, extension_length=extension_length, offset_from_wall=offset_from_wall))

        if number_of_steps is None:
            raise ValueError("Missing 'num_steps' in stair case item.")
        if width is None:
            raise ValueError("Missing 'width' in stair case item.")
        if riser_height is None:
            raise ValueError("Missing 'riser_height' in stair case item.")
        if tread_depth is None:
            raise ValueError("Missing 'tread_depth' in stair case item.")

        return StairCase(name, number_of_steps, width, tread_depth, riser_height, 
                         tactile_strip_attached, tactile_strip_before_stairs_distance, tactile_strip_after_stairs_distance, 
                         handRails
                )