import math

# Parameters
ramp_length = 4.0
ramp_width = 1.0
ramp_thickness = 0.2
ramp_angle_deg = 15

alley_length = 5.0

# Derived values
ramp_pitch = math.radians(ramp_angle_deg)

# Ramp center position
ramp_x = math.cos(ramp_pitch) * (ramp_length / 2.0)
ramp_z = math.sin(ramp_pitch) * (ramp_length / 2.0)

# Ramp top edge position
top_x = ramp_length*math.cos(ramp_pitch)
top_z = ramp_length*math.sin(ramp_pitch)

deflection = 0.02
# Alleyway center position
alley_x = top_x + alley_length / 2.0 - deflection
alley_z = top_z


rampWithAlley = f"""
<model name="ramp{n}">
      <pose>{ramp_x} 0 {ramp_z} 0 {-ramp_pitch} 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>{ramp_length} {ramp_width} {ramp_thickness}</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>{ramp_length} {ramp_width} {ramp_thickness}</size>
            </box>
          </geometry>
          <material>
            <ambient>0.7 0.4 0.2 1</ambient>
            <diffuse>0.7 0.4 0.2 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="alleyway{n}">
      <pose>{alley_x} 0 {alley_z} 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>{alley_length} {ramp_width} {ramp_thickness}</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>{alley_length} {ramp_width} {ramp_thickness}</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.5 1</ambient>
            <diffuse>0.5 0.5 0.5 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
"""

# SDF template
sdf_template = f"""<sdf version="1.7">
  <world name="default">
    <include>
      <uri>model://ground_plane</uri>
    </include>
    <include>
      <uri>model://sun</uri>
    </include>

    
  </world>
</sdf>
"""

# Save file
with open("ramp_with_alley.sdf", "w") as f:
    f.write(sdf_template)

print("SDF file 'ramp_with_alley.sdf' generated successfully!")
