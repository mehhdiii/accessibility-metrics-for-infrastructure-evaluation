import mysql.connector
import io
import json
import open3d as o3d
from PIL import Image

# --- MySQL config ---
MYSQL_HOST = "mysql"
MYSQL_USER = "stairuser"
MYSQL_PASSWORD = "stairpass"
MYSQL_DB = "stairs_db"
MYSQL_PORT = 3306

# --- Connect to MySQL ---
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
    port=MYSQL_PORT
)
cursor = conn.cursor(dictionary=True)

# --- Get latest point cloud record ---
cursor.execute("SELECT * FROM pointclouds ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
cursor.close()
conn.close()

if row is None:
    raise ValueError("No point cloud found in DB")

# --- Save Point Cloud to PCD file ---
with io.BytesIO(row['data']) as f:
    pc = o3d.io.read_point_cloud(f)

pcl_filename = f"{row['name']}.pcd"
o3d.io.write_point_cloud(pcl_filename, pc)
print(f"Saved point cloud to {pcl_filename}")

# --- Save Image to PNG ---
image_bytes = row['image_2d']
image = Image.open(io.BytesIO(image_bytes))
img_filename = f"{row['name']}.png"
image.save(img_filename)
print(f"Saved image to {img_filename}")

# --- Save Camera Parameters to JSON ---
camera_params = row.get('camera_params')
if camera_params:
    cam_filename = f"{row['name']}_camera.json"
    with open(cam_filename, 'w') as f:
        f.write(camera_params)
    print(f"Saved camera parameters to {cam_filename}")
else:
    print("No camera parameters found in the record")
