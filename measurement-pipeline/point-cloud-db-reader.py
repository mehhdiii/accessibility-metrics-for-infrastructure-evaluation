import mysql.connector
import open3d as o3d
import io
import tempfile

# Connect to MySQL
conn = mysql.connector.connect(
    host="mysql",
    user="stairuser",
    password="stairpass",
    database="stairs_db"
)
cursor = conn.cursor()

# Fetch a point cloud by name or frame_number
cursor.execute("SELECT data FROM pointclouds WHERE id=2")
row = cursor.fetchone()
cursor.close()
conn.close()

if row is None:
    raise ValueError("No point cloud found for the given name/frame.")

# Get the blob bytes
pcd_bytes = row[0]

# Write to a temporary file
with tempfile.NamedTemporaryFile(suffix=".pcd") as tmp_file:
    tmp_file.write(pcd_bytes)
    tmp_file.flush()  # ensure all data is written
    # Read point cloud from temporary file
    pcd = o3d.io.read_point_cloud(tmp_file.name)

# Output file
output_file = "point-clouds/frame_db.pcd"
o3d.io.write_point_cloud(output_file, pcd)
