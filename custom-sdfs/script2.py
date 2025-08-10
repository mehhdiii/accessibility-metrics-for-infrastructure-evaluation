import math
from jinja2 import Template

# Load template
with open("ramp.sdf") as f:
    template = Template(f.read())

# Parameters
slopes_deg = [5, 10, 15, 20]  # slope angles to generate
ramp_length_surface = 2.0      # meters along the ramp surface (L)
ramp_width = 1.0               # meters
ramp_thickness = 0.05          # meters
gap_fix = 0.04                 # meters to slightly sink ramp to avoid bump
alley_length = 2.0  # length of alleyway after ramp

for slope_deg in slopes_deg:
    slope_rad = math.radians(slope_deg)

    # Compute ramp height and horizontal length projection
    ramp_height = ramp_length_surface * math.sin(slope_rad)
    ramp_length_horizontal = ramp_length_surface * math.cos(slope_rad)

    # Pose:
    # X: place ramp so its start edge is at x=0
    ramp_x = (ramp_length_surface / 2.0) * math.cos(slope_rad)

    # Z: raise ramp so bottom edge is flush with ground, minus small gap fix
    ramp_z = (ramp_thickness / 2.0) + (ramp_length_surface / 2.0) * math.sin(slope_rad) - gap_fix

    # X position: ramp_x + half ramp length horizontal + half alley length
    ramp_end_x = ramp_x + (ramp_length_horizontal / 2.0)
    alley_x = ramp_end_x + (alley_length / 2.0)

    # Z position: ramp top surface height = ramp_z + half thickness + vertical offset from slope
    alley_z = ramp_z + (ramp_thickness / 2.0) + ramp_height
    
    sdf_content = template.render(
        ramp_x=round(ramp_x, 3),
        ramp_z=round(ramp_z, 3),
        ramp_pitch=round(slope_rad, 4),
        ramp_length=ramp_length_surface,
        ramp_width=ramp_width,
        ramp_thickness=ramp_thickness,
        alley_x=-round(alley_x, 3),
        alley_z=round(alley_z, 3),
        alley_length=alley_length
    )

    filename = f"world_slope_{slope_deg}.sdf"
    with open(filename, "w") as f:
        f.write(sdf_content)
    print(f"Generated {filename}")
