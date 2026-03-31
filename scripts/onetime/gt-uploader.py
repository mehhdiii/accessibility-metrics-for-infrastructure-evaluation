import json
import mysql.connector

# -------- Database Config -------- #
DB_CONFIG = {
    "host": "localhost",
    "user": "stairuser",
    "password": "stairpass",
    "database": "stairs_db"
}

INPUT_FILE = "world-generator/scripts/specifications/staircases.json"


def insert_staircases():
    # ---- Load JSON ----
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    valid = data["valid_staircases"]
    invalid = data["invalid_staircases"]

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO gtStaircase (
            name, description, root_name, type, width, num_steps, riser_height,
            tread_depth, tactile_strips_before_length, tactile_strips_after_length,
            parapet_height, parapet_max_opening_diameter, handrails_side,
            handrails_height, handrails_extension_length, handrails_offset_from_wall
        )
        VALUES (%(name)s, %(description)s, %(root_name)s, %(type)s, %(width)s, %(num_steps)s,
                %(riser_height)s, %(tread_depth)s, %(tactile_strips_before_length)s,
                %(tactile_strips_after_length)s, %(parapet_height)s,
                %(parapet_max_opening_diameter)s, %(handrails_side)s,
                %(handrails_height)s, %(handrails_extension_length)s,
                %(handrails_offset_from_wall)s)
    """

    # ---- Process VALID staircases ----
    for idx, item in enumerate(valid, start=1):
        new_name = f"exp_1_valid{idx}"
        root = item["root"]
        handrail = root["handrails"][0] if root["handrails"] else {}

        record = {
            "name": new_name,
            "description": item.get("description"),

            "root_name": root.get("name"),
            "type": root.get("type"),
            "width": root.get("width"),
            "num_steps": root.get("num_steps"),
            "riser_height": root.get("riser_height"),
            "tread_depth": root.get("tread_depth"),

            "tactile_strips_before_length": root["tactile_strips"]["before_length"],
            "tactile_strips_after_length": root["tactile_strips"]["after_length"],

            "parapet_height": root["parapet"]["height"],
            "parapet_max_opening_diameter": root["parapet"]["max_opening_diameter"],

            "handrails_side": handrail.get("side"),
            "handrails_height": handrail.get("height"),
            "handrails_extension_length": handrail.get("extension_length"),
            "handrails_offset_from_wall": handrail.get("offset_from_wall")
        }

        cursor.execute(insert_query, record)

    # ---- Process INVALID staircases ----
    for idx, item in enumerate(invalid, start=1):
        new_name = f"exp_1_invalid{idx}"
        root = item["root"]
        handrail = root["handrails"][0] if root["handrails"] else {}

        record = {
            "name": new_name,
            "description": item.get("description"),

            "root_name": root.get("name"),
            "type": root.get("type"),
            "width": root.get("width"),
            "num_steps": root.get("num_steps"),
            "riser_height": root.get("riser_height"),
            "tread_depth": root.get("tread_depth"),

            "tactile_strips_before_length": root["tactile_strips"]["before_length"],
            "tactile_strips_after_length": root["tactile_strips"]["after_length"],

            "parapet_height": root["parapet"]["height"],
            "parapet_max_opening_diameter": root["parapet"]["max_opening_diameter"],

            "handrails_side": handrail.get("side"),
            "handrails_height": handrail.get("height"),
            "handrails_extension_length": handrail.get("extension_length"),
            "handrails_offset_from_wall": handrail.get("offset_from_wall")
        }

        cursor.execute(insert_query, record)

    conn.commit()
    cursor.close()
    conn.close()

    print("All staircases inserted successfully!")


if __name__ == "__main__":
    insert_staircases()
