import json
import math
from Ramp import Ramp
from Platform import Platform
from RampSpecsReader import RampSpecsReader
from RampMapper import RampMapper
from PlatformMapper import PlatformMapper
from enums import ElementType

import os 
from dotenv import load_dotenv

result = load_dotenv()

class SDFGenerator:
    def __init__(self):
        self.y_offset = os.getenv("Y_OFFSET", 2.0)
        self.required_assets = set()
        self.models = []

        self.sdf_string = ''

    def parseTree(self, root, index):
        # Implement parsing logic here
        child = root
        ramp = None
        while (True):
            if child is None:
                break

            # print(f"child: {child}")
            if child.get("type") == ElementType.RAMP.value:
                # Process ramp
                ramp = RampMapper.rampMapper(child)
                ramp.init(index)
                self.required_assets.add(ramp.asset_name)
                self.sdf_string += ramp.render()

            elif child.get("type") == ElementType.PLATFORM.value:
                # Process platform
                if (not ramp):
                    raise ValueError("Platform specified without a preceding ramp.")
                platform = PlatformMapper.platformMapper(child)
                platform.init(ramp)
                self.required_assets.add(platform.asset_name)   
                self.sdf_string += platform.render()
                # reinitialize ramp to None
                ramp = None
            child = child.get("child")




    def place_in_world(self, sdf_models): 
        sdf_world = f"""<sdf version="1.7">
        <world name="default">
            <include>
            <uri>model://ground_plane</uri>
            </include>
            <include>
            <uri>model://sun</uri>
            </include>

            {sdf_models}

        </world>
        </sdf>
        """
        return sdf_world
    
    def generate(self, ramps, model_type):
        for index, specs in enumerate(ramps):
            print(specs.get("name"))
            root = specs.get("root")
            self.parseTree(root, index)
        return self.sdf_string


rampSpecsReader = RampSpecsReader()
# Create SDFGenerator instance
sdf_generator = SDFGenerator()

model_string = sdf_generator.generate(rampSpecsReader.validRamps, "valid")
# model_string = sdf_generator.write_ramps_with_platform(model_string, invalid_ramps, "invalid")

# Generate final SDF world
sdf_world = sdf_generator.place_in_world(model_string)
print(sdf_world)
from pprint import pprint
# pprint(sdf_generator.required_assets)
