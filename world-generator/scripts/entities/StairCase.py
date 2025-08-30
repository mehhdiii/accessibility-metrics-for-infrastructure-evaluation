import os
import uuid
from entities.TactileStrip import TactileStrip
from entities.HandRail import HandRail
from entities.Stair import Stair
from entities.Wall import Wall
from typing import TypedDict
from entities.shared import HandrailSpecs
import math

class StairCase:
    def __init__(self, name: str, numberOfSteps: int, width: float, tread_depth: float, riser_height: float, tactile_strip_attached: bool = False, tactile_strip_before_stairs_distance: float = 0.0, tactile_strip_after_stairs_distance: float = 0.0, handrailSpecs: list[HandrailSpecs] = []):
        self.name = name
        self.id = str(uuid.uuid4())
        self.numberOfSteps = numberOfSteps
        self.width = width
        self.tread_depth = tread_depth
        self.riser_height = riser_height
        self.stairs: list[Stair] = []
        self.y_offset: float = float(os.getenv("Y_OFFSET", -1.0))
        self.x_offset: float = float(os.getenv("X_OFFSET", -1.0))
        
        self.tactile_strip_attached: bool = tactile_strip_attached
        self.tactile_strip_before_stairs_distance: float = tactile_strip_before_stairs_distance
        self.tactile_strip_after_stairs_distance: float = tactile_strip_after_stairs_distance
        self.tactile_strip_before: TactileStrip | None = None
        self.tactile_strip_after: TactileStrip | None = None

        self.handrailSpecs = handrailSpecs
        self.handrails: list[HandRail] = []


        if (self.y_offset == -1.0):
            raise ValueError("Y_OFFSET environment variable is not set.")
        if (self.x_offset == -1.0):
            raise ValueError("X_OFFSET environment variable is not set.")

    def init(self, yIndex: int, xIndex: int):

        self.position = self._calculate_position(yIndex, xIndex)
        end_pose = self.initialize_stair()
        if self.tactile_strip_attached:
           self.initialize_tactile_strips(end_pose)
        
        if len(self.handrailSpecs) > 0:
            self.initialize_handrails()
        self.initializeWalls()

    @property
    def asset_name(self):
        assetNames = ''
        for step in self.stairs:
            assetNames += step.asset_name + ', '
        return assetNames

    def _calculate_position(self, yIndex: int, xIndex: int):
        # Calculate the position based on the indices
        x: float =  xIndex * self.x_offset  # calculation for x position
        y: float = yIndex * self.y_offset    # calculation for y position
        z: float = 0.0               # Fixed z position
        return [x, y, z, 0.0, 0.0, 0.0]
    
    def initialize_handrails(self):
        for i in self.handrailSpecs:
            #calculate total length along the stairs: 
            total_length_along_stair = ((self.numberOfSteps*self.riser_height)**2 + (self.numberOfSteps*self.tread_depth)**2)**0.5
            height = i["height"]
            protruding_length = i["extension_length"]
            lefthandrail = HandRail(f"handrail_{self.id}_{i}", total_length_along_stair + 2*protruding_length, height)
            righthandrail = HandRail(f"handrail_{self.id}_{i}", total_length_along_stair + 2*protruding_length, height)

            #place at the center left and center right of the staircase
            angle = -math.atan2(self.numberOfSteps*self.riser_height, self.numberOfSteps*self.tread_depth)
            handrail_position = [self.position[0]+self.tread_depth*self.numberOfSteps/2, self.position[1] - self.width/2, self.position[2] + self.riser_height*self.numberOfSteps/2, 0, angle, 0]
            lefthandrail.init(handrail_position)
            handrail_position = [self.position[0]+self.tread_depth*self.numberOfSteps/2, self.position[1] + self.width/2, self.position[2] + self.riser_height*self.numberOfSteps/2, 0, angle, 0]
            righthandrail.init(handrail_position)
            
            #append to master list:
            self.handrails.append(lefthandrail)
            self.handrails.append(righthandrail)

    def initialize_tactile_strips(self, end_pose):
        if (self.position is None):
            raise ValueError("StairCase position is not set.")

        #create tactile strips with dim: (l, w) = (width/2, width)
        self.tactile_strip_before = TactileStrip(f"tactile_strip_before_{self.id}", self.width/2, self.width)
        self.tactile_strip_before.init([self.position[0] - self.tactile_strip_before_stairs_distance - self.tactile_strip_before.length/2, self.position[1], self.position[2]])
        self.tactile_strip_after = TactileStrip(f"tactile_strip_after_{self.id}", self.width/2, self.width)
        self.tactile_strip_after.init([end_pose[0] + self.tactile_strip_after_stairs_distance + self.tactile_strip_after.length/2, end_pose[1], end_pose[2]])

    def initialize_stair(self):
        if (self.numberOfSteps <= 0):
            raise ValueError("Number of steps must be greater than 0.")
        self.stairs = [] # always clear before filling it up:
        last_stair = None
        for i in range(self.numberOfSteps):
            stair = Stair(f"stair_{self.id}_{i}", self.width, self.tread_depth, self.riser_height)
            
            if (last_stair is None):
                # this is the first riser
                stair_position: list[float] = [self.position[0] + self.tread_depth/2, self.position[1], self.position[2]]
            else:
                if (last_stair.position is None):
                    raise ValueError("Last stair position is not set.")
                stair_position: list[float] = [last_stair.position[0] + self.tread_depth, last_stair.position[1], last_stair.position[2]+self.riser_height]            
            stair.init(stair_position)
            
            self.stairs.append(stair)
            last_stair = stair

        if (last_stair is None):
            return
        if (last_stair.position is None):
            raise ValueError("Last tread position is not set.")
        
        return [last_stair.position[0] + last_stair.depth, last_stair.position[1], last_stair.position[2]+last_stair.height]
    
    def initializeWalls(self):
        self._leftWall = Wall(f"{self.name}_left", length=self.dimensions[0]) 
        self._rightWall = Wall(f"{self.name}_right", length=self.dimensions[0])

        if (self.position is None):
            raise ValueError("Widening position is not set.")

        #initialize the left wall to be W/2 from the center of widening
        self._leftWall.init([self.position[0]+self.dimensions[0]/2, self.position[1] - (self.width / 2) - self._leftWall.thickness/2, self.position[2]])
        #initialize the right wall to be W/2 from the center of widening
        self._rightWall.init([self.position[0]+self.dimensions[0]/2, self.position[1] + (self.width / 2) + self._rightWall.thickness/2, self.position[2]])

    @property
    def dimensions(self):
        """Return the dimensions of the stair as a tuple (length, height, thickness)."""
        return (self.tread_depth*self.numberOfSteps, self.riser_height*self.numberOfSteps, self.width)

    @property
    def pose(self):
        if not self.position:
            raise ValueError("StairCase position is not set.")
        if len(self.position) < 3:
            raise ValueError("StairCase position must have at least 3 elements.")
        return tuple(self.position)

    def __repr__(self):
        return f"StairCase(stepCount={self.numberOfSteps}, position={self.position})"

    def render(self):
        rendered = self.tactile_strip_before.render() if self.tactile_strip_before is not None else ''
        rendered += self.tactile_strip_after.render() if self.tactile_strip_after is not None else ''
        for i in self.handrails:
            rendered += i.render()

        for stair in self.stairs:
            rendered += stair.render()
        rendered += self._leftWall.render() if self._leftWall is not None else ''
        rendered += self._rightWall.render() if self._rightWall is not None else ''
        return rendered