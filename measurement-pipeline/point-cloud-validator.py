import open3d as o3d
import numpy as np

pcd = o3d.io.read_point_cloud("point-clouds/frame_db.pcd")
output_file = "point-clouds/frame_filtered.pcd"

print(pcd)  # prints number of points and basic info
print(np.asarray(pcd.points)[:5])  # shows first 5 points


print("Min bound:", pcd.get_min_bound())
print("Max bound:", pcd.get_max_bound())
print("Number of points:", len(pcd.points))


points = np.asarray(pcd.points)

# Remove points with inf or nan
mask = np.isfinite(points).all(axis=1)
filtered_points = points[mask]

# Create a new PointCloud with valid points
pcd_clean = o3d.geometry.PointCloud()
pcd_clean.points = o3d.utility.Vector3dVector(filtered_points)

print("Number of valid points:", len(filtered_points))
print("Min bound:", pcd_clean.get_min_bound())
print("Max bound:", pcd_clean.get_max_bound())

print(np.asarray(pcd_clean.points).max(axis=0))
print(np.asarray(pcd_clean.points).min(axis=0))

# --- Transformation from TF echo ---
# Translation vector
t = np.array([0.0, 0.0, 0.0])

# Rotation from RPY: [-0.000, -1.571, 1.571] radians
roll, pitch, yaw = -0.0, -1.571, 1.571

# Build rotation matrices
Rx = np.array([[1, 0, 0],
               [0, np.cos(roll), -np.sin(roll)],
               [0, np.sin(roll), np.cos(roll)]])

Ry = np.array([[np.cos(pitch), 0, np.sin(pitch)],
               [0, 1, 0],
               [-np.sin(pitch), 0, np.cos(pitch)]])

Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0],
               [np.sin(yaw), np.cos(yaw), 0],
               [0, 0, 1]])

# Combined rotation
R = Rz @ Ry @ Rx

# Build full 4x4 transformation
T = np.eye(4)
T[:3, :3] = R
T[:3, 3] = t

# Apply transformation to point cloud
pcd_clean.transform(T)

# Flip axes to match RViz optical frame (+X forward, +Y left, +Z up)
points = np.asarray(pcd_clean.points)
points[:, [0, 1, 2]] = points[:, [0, -1, -2]]  # flip Y and Z
pcd_clean.points = o3d.utility.Vector3dVector(points)

R_flip = pcd_clean.get_rotation_matrix_from_xyz((3*np.pi/2, np.pi, 0))
pcd_clean.rotate(R_flip, center=pcd_clean.get_center())

# Visualize
o3d.visualization.draw_geometries([pcd_clean])


o3d.io.write_point_cloud(output_file, pcd_clean)

# vis = o3d.visualization.Visualizer()
# vis.create_window(visible=False)
# vis.add_geometry(pcd)
# vis.poll_events()
# vis.update_renderer()
# vis.capture_screen_image("point-clouds/frame.png")
# vis.destroy_window()
