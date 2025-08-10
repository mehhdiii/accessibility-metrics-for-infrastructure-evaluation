import json
import math

# ---------- CONFIG ----------
INPUT_JSON = "ramps.json"
OUTPUT_SDF = "ramps_generated.sdf"
SPACING_Y = 3.0  # meters between each ramp-alley pair
DEFLECTION = 0.02
# ---------------------------

def ramp_and_alley_sdf(n, name, length, width, thickness, slope=None, angle_deg=None, alley_length=5.0, y_offset=0):
    """
    Returns an SDF snippet for one ramp with an alley, positioned along the y-axis.
    Slope can be given as ratio (rise/run) or angle_deg (degrees).
    """
    # Convert slope to angle in radians
    if slope is not None:
        ramp_pitch = math.atan(slope)
    elif angle_deg is not None:
        ramp_pitch = math.radians(angle_deg)
    else:
        raise ValueError("Either slope or angle_deg must be provided")

    # Ramp center position
    ramp_x = math.cos(ramp_pitch) * (length / 2.0)
    ramp_z = math.sin(ramp_pitch) * (length / 2.0)

    # Ramp top edge position
    top_x = length * math.cos(ramp_pitch)
    top_z = length * math.sin(ramp_pitch)

    # Alleyway center position
    alley_x = top_x + alley_length / 2.0 - DEFLECTION
    alley_z = top_z

    return f"""
    <model name="{name}_ramp_{n}">
      <pose>{ramp_x} {y_offset} {ramp_z} 0 {-ramp_pitch} 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>{length} {width} {thickness}</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>{length} {width} {thickness}</size>
            </box>
          </geometry>
          <material>
            <ambient>0.7 0.4 0.2 1</ambient>
            <diffuse>0.7 0.4 0.2 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="{name}_alley_{n}">
      <pose>{alley_x} {y_offset} {alley_z} 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>{alley_length} {width} {thickness}</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>{alley_length} {width} {thickness}</size>
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


def main():
    with open(INPUT_JSON, "r") as f:
        data = json.load(f)

    sdf_models = ""

    # Place valid ramps on positive Y side
    for i, ramp in enumerate(data.get("valid_ramps", [])):
        sdf_models += ramp_and_alley_sdf(
            n=i,
            name=ramp["name"].replace(" ", "_"),
            length=ramp["length"],
            width=ramp["width"],
            thickness=ramp["thickness"],
            slope=ramp.get("slope"),
            angle_deg=ramp.get("angle_deg"),
            alley_length=5.0,
            y_offset=i * SPACING_Y
        )

    # Place invalid ramps on negative Y side
    for i, ramp in enumerate(data.get("invalid_ramps", [])):
        sdf_models += ramp_and_alley_sdf(
            n=i,
            name=ramp["name"].replace(" ", "_"),
            length=ramp["length"],
            width=ramp["width"],
            thickness=ramp["thickness"],
            slope=ramp.get("slope"),
            angle_deg=ramp.get("angle_deg"),
            alley_length=5.0,
            y_offset=-(i * SPACING_Y) - SPACING_Y
        )

    # Final SDF
    sdf_template = f"""<sdf version="1.7">
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
    with open(OUTPUT_SDF, "w") as f:
        f.write(sdf_template)

    print(f"SDF file '{OUTPUT_SDF}' generated successfully!")


if __name__ == "__main__":
    main()
