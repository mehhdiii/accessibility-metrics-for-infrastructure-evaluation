from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()


class StairParams(BaseModel):
    step_depth: float          # cm
    step_height: float         # cm (riser)
    step_width: float          # cm
    stair_parts: int
    risers: int
    treads: int

    class Config:
        extra = "ignore"  # <-- ignore any extra fields in request


@app.post("/check")
async def check_stairs(params: StairParams) -> Dict:
    # Extract values
    h = params.step_height
    p = params.step_depth
    w = params.step_width

    # --- Italian decree (Art. 8.1.10) ---
    checks = {}

    # Minimum width for public stairway (≥ 1.20 m)
    checks["width_ok"] = w >= 120

    # Minimum tread (≥ 30 cm)
    checks["tread_ok"] = p >= 30

    # Riser–tread relation (2h + p = 62–64 cm)
    checks["riser_tread_relation_ok"] = 62 <= (2 * h + p) <= 64

    # Step slope consistency (approx. 20–38° typical comfort)
    # checks["stair_angle_ok"] = 20 <= params.stair_angle_deg <= 38

    # Placeholder for unavailable decree parameters
    # (these exist in decree but not in input)
    missing_params = {
        "step_profile_ok": False,            # continuous rounded or 2–2.5 cm nosing
        "floor_marking_ok": False,           # tactile strip 30 cm before/after stairs
        "parapet_height_ok": False,          # ≥ 100 cm
        "sphere_block_ok": False,            # ≤ 10 cm sphere cannot pass
        "handrail_height_ok": False,         # 0.90–1.00 m (or 0.75 m second)
        "handrail_extension_ok": False,      # +30 cm beyond first/last step
        "handrail_clearance_ok": False,      # ≥ 4 cm from wall
    }

    checks.update(missing_params)

    notes = {
        "width_ok": "Step width ≥ 1.20 m",
        "tread_ok": "Tread depth ≥ 30 cm",
        "riser_tread_relation_ok": "2×riser + tread between 62 cm and 64 cm",
        "stair_angle_ok": "Stair slope angle ≈ 20–38° typical comfort",
        "step_profile_ok": "Rounded or protruding 2–2.5 cm (not provided → false)",
        "floor_marking_ok": "Tactile strip 30 cm before/after stairs (not provided → false)",
        "parapet_height_ok": "Parapet ≥ 100 cm & ≤ 10 cm sphere impassable (not provided → false)",
        "sphere_block_ok": "Must block 10 cm sphere (not provided → false)",
        "handrail_height_ok": "Handrail 0.90–1.00 m (0.75 m second) (not provided → false)",
        "handrail_extension_ok": "Handrail extends 30 cm beyond first/last step (not provided → false)",
        "handrail_clearance_ok": "≥ 4 cm from wall (not provided → false)"
    }

    return {
        "compliance": checks,
        "notes": notes
    }
