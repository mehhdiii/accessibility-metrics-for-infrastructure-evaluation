import json
import math
from Ramp import Ramp
from Platform import Platform
from RampSpecsReader import RampSpecsReader
from RampMapper import RampMapper
from PlatformMapper import PlatformMapper
from enums import ElementType, RampClassification

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
        platform = None
        while (True):
            if child is None:
                break

            # print(f"child: {child}")
            if child.get("type") == ElementType.RAMP.value:
                # Process ramp
                ramp = RampMapper.rampMapper(child)
                if (platform):
                    # print("Setting parent platform for ramp")
                    ramp.parentPlatform = platform
                ramp.init(index)
                if (index < 0):
                    self.required_assets.add(ramp.asset_name)
                
                self.sdf_string += ramp.render()
                platform = None  # Reset platform after processing ramp

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
            <!-- Ground plane from Fuel -->
            <include>
            <uri>https://fuel.gazebosim.org/1.0/openrobotics/models/Ground%20Plane</uri>
            </include>

                <!-- Sun from Fuel -->
            <include>
            <uri>https://fuel.gazebosim.org/1.0/openrobotics/models/Sun</uri>
            </include>

            {sdf_models}

        </world>
        </sdf>
        """
        return sdf_world
    
    def generate(self, ramps, model_type):
        for index, specs in enumerate(ramps):
            idx = index + 1
            if (model_type == RampClassification.INVALID.value):
                idx = -idx
            root = specs.get("root")
            self.parseTree(root, idx)
            print(f"Parsed {model_type} ramp: {specs.get('name')} at index {idx}")
        return self.sdf_string


rampSpecsReader = RampSpecsReader()
# Create SDFGenerator instance
sdf_generator = SDFGenerator()

model_string = sdf_generator.generate(rampSpecsReader.validRamps, RampClassification.VALID.value)
model_string = sdf_generator.generate(rampSpecsReader.invalidRamps, RampClassification.INVALID.value)

# Generate final SDF world
sdf_world = sdf_generator.place_in_world(model_string)
print(sdf_world)
from pprint import pprint
# pprint(sdf_generator.required_assets)
