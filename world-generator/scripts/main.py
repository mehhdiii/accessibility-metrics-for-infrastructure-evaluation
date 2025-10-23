#readers
from readers.RampSpecsReader import RampSpecsReader
from readers.CorridorSpecsReader import CorridorSpecsReader
from readers.StairCaseSpecsReader import StairCaseSpecsReader

#mappers
from mappers.RampMapper import RampMapper
from mappers.PlatformMapper import PlatformMapper
from mappers.CorridorMapper import CorridorMapper
from mappers.WideningMapper import WideningMapper
from mappers.StairCaseMapper import StairCaseMapper

#const enums
from enums import ElementType, SpecClassification

#load env variables
import os
from dotenv import load_dotenv
result = load_dotenv()

class SDFGenerator:
    def __init__(self):
        self.required_assets = set()
        self.models = []

        self.sdf_string = ''

    def parseTree(self, root, y_index, x_index):
        # Implement parsing logic here
        child = root
        #ramp platform
        ramp = None
        platform = None

        # corridor
        corridor = None
        widening = None
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
                ramp.init(y_index)
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

            elif child.get("type") == ElementType.CORRIDOR.value:
                corridor = CorridorMapper.corridorMapper(child)
                if (widening):
                    corridor._previous_widening = widening
                corridor.init(y_index, x_index)
                self.required_assets.add(corridor.asset_name)
                self.sdf_string += corridor.render()
                widening = None  # Reset widening after processing corridor

            elif child.get("type") == ElementType.WIDENING.value:
                widening = WideningMapper.wideningMapper(child)
                if (not corridor):
                    raise ValueError("Widening specified without a preceding corridor.")
                widening.init(y_index, x_index, corridor)
                self.required_assets.add(widening.asset_name)
                self.sdf_string += widening.render()
                corridor = None  # Reset corridor after processing widening
            elif child.get("type") == ElementType.STAIRCASE.value:
                staircase = StairCaseMapper.StairCaseMapper(child)
                staircase.init(y_index, x_index)
                self.required_assets.add(staircase.asset_name)
                self.sdf_string += staircase.render()
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
    def write_to_file(self, sdf_string):
        fileName = os.getenv("OUTPUT_FILE")
        if fileName is None:
            raise ValueError("OUTPUT_FILE environment variable is not set.")
        with open(fileName, "w") as f:
            f.write(sdf_string)

    def generate(self, ramps, model_type, x_index):
        for index, specs in enumerate(ramps):
            y_index = index + 1
            if (model_type == SpecClassification.INVALID.value):
                y_index = -y_index
            root = specs.get("root")
            self.parseTree(root, y_index, x_index)
            print(f"Parsed {model_type} ramp: {specs.get('name')} at index {y_index}")
        return self.sdf_string


# read ramp specs:
rampSpecsReader = RampSpecsReader()
# read corridor specs:
corridorSpecsReader = CorridorSpecsReader()
# read staircase specs:
staircaseSpecsReader = StairCaseSpecsReader()

# Create SDFGenerator instance
sdf_generator = SDFGenerator()

#generate ramp sdfs
# sdf_generator.generate(rampSpecsReader.validRamps, SpecClassification.VALID.value, x_index=0)
# sdf_generator.generate(rampSpecsReader.invalidRamps, SpecClassification.INVALID.value, x_index=0)


# # #generate corridor sdfs
# sdf_generator.generate(corridorSpecsReader.validCorridors, SpecClassification.VALID.value, x_index=0)
# sdf_generator.generate(corridorSpecsReader.invalidCorridors, SpecClassification.INVALID.value, x_index=0)

# generate staircase sdfs
sdf_generator.generate(staircaseSpecsReader.validStairCases, SpecClassification.VALID.value, x_index=0)
sdf_generator.generate(staircaseSpecsReader.invalidStairCases, SpecClassification.INVALID.value, x_index=0)

# Generate final SDF world
sdf_world = sdf_generator.place_in_world(sdf_generator.sdf_string)
sdf_generator.write_to_file(sdf_world)
print("written to output successfully!")
from pprint import pprint
# pprint(sdf_generator.required_assets)
