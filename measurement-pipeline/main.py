import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# 1. Load point cloud
# -------------------------------
pcd = o3d.io.read_point_cloud("point-clouds/frame_filtered.pcd")  # replace with your file

# -------------------------------
# 2. Preprocess
# -------------------------------
pcd_down = pcd.voxel_down_sample(voxel_size=0.01)
pcd_clean, ind = pcd_down.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)

# -------------------------------
# 3. Floor segmentation
# -------------------------------
plane_model, inliers = pcd_clean.segment_plane(distance_threshold=0.001,
                                               ransac_n=3,
                                               num_iterations=1000)
floor_cloud = pcd_clean.select_by_index(inliers)
stairs_cloud = pcd_clean.select_by_index(inliers, invert=True)

# 3. Remove large vertical planes (walls) when no floor is present
# -------------------------------
pts = np.asarray(pcd_clean.points)
mask = np.ones(len(pts), dtype=bool)

max_planes = 6
min_inliers = 200        # ignore tiny planes
distance_threshold = 0.01
z_dot_thresh = 0.3       # plane normal z component must be small => vertical plane

removed_planes = 0
for _ in range(max_planes):
    idxs = np.where(mask)[0]
    if len(idxs) < min_inliers:
        break
    tmp = o3d.geometry.PointCloud()
    tmp.points = o3d.utility.Vector3dVector(pts[idxs])

    plane_model, inliers = tmp.segment_plane(distance_threshold=distance_threshold,
                                             ransac_n=3,
                                             num_iterations=1000)
    if len(inliers) == 0:
        break

    orig_inliers = idxs[inliers]
    normal = np.array(plane_model[:3])
    normal = normal / np.linalg.norm(normal)

    # detect vertical planes (walls): normal's Z component near zero
    if abs(normal[2]) < z_dot_thresh and len(orig_inliers) >= min_inliers:
        mask[orig_inliers] = False
        removed_planes += 1
    else:
        # not a vertical plane, remove it from consideration to avoid infinite loop
        mask[orig_inliers] = False

# remaining points are treated as candidate stairs (no floor expected)
remaining_idx = np.where(mask)[0]
stairs_cloud = pcd_clean.select_by_index(remaining_idx)

print(f"Removed {removed_planes} large vertical plane(s). Remaining points: {len(remaining_idx)}")



# # 4. Cluster risers (improved)
# # -------------------------------
# # estimate normals (needed to detect vertical surfaces)
# stairs_cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05,
#                                                                                max_nn=30))

# # compute median nearest-neighbour distance (sample up to 500 points)
# tree = o3d.geometry.KDTreeFlann(stairs_cloud)
# sample_n = min(500, len(stairs_cloud.points))
# nn_dists = []
# for i in range(sample_n):
#     _, idx, dist = tree.search_knn_vector_3d(stairs_cloud.points[i], 2)
#     if len(dist) > 1:
#         nn_dists.append(np.sqrt(dist[1]))
# median_nn = np.median(nn_dists) if len(nn_dists) > 0 else 0.02

# # choose eps relative to the median spacing (tune multiplier if needed)
# eps = max(0.01, median_nn * 3.0)
# min_points = 20  # lower than before because risers can be small/fractured

# # filter points whose normals indicate vertical surfaces (riser candidates)
# normals = np.asarray(stairs_cloud.normals)
# vertical_mask_idx = np.where(np.abs(normals[:, 2]) < 0.5)[0]  # tune threshold (0.2-0.4)
# vertical_cloud = stairs_cloud.select_by_index(vertical_mask_idx)
# o3d.visualization.draw_geometries([vertical_cloud])

# print(f"Clustering {len(vertical_cloud.points)} vertical-candidate points (eps={eps:.3f}, min_pts={min_points})")

# with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug) as cm:
#     v_labels = np.array(vertical_cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))

# # map labels back into an array aligned with stairs_cloud points
# labels = np.full(len(stairs_cloud.points), -1, dtype=int)
# labels[vertical_mask_idx] = v_labels

# max_label = labels.max()
# if max_label >= 0:
#     print(f"Detected {max_label+1} riser clusters")
# else:
#     print("No clusters found; try lowering eps or min_points, or relaxing vertical normal threshold")


# 4. Cluster risers (PCA-filtered DBSCAN on whole stairs_cloud)
# -------------------------------
# estimate normals (still useful but we won't pre-filter on them)
stairs_cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05,
                                                                               max_nn=30))
o3d.visualization.draw_geometries([stairs_cloud])

# compute median NN spacing to pick eps
tree = o3d.geometry.KDTreeFlann(stairs_cloud)
sample_n = min(500, len(stairs_cloud.points))
nn_dists = []
for i in range(sample_n):
    _, idx, dist2 = tree.search_knn_vector_3d(stairs_cloud.points[i], 2)
    if len(dist2) > 1:
        nn_dists.append(np.sqrt(dist2[1]))
median_nn = np.median(nn_dists) if len(nn_dists) > 0 else 0.02

eps = max(0.01, median_nn * 3.0)
min_points = 6  # allow smaller clusters to form

print(f"Running DBSCAN on whole stairs_cloud (eps={eps:.3f}, min_pts={min_points})")
with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug):
    all_labels = np.array(stairs_cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))

accepted_labels = set()
for lbl in np.unique(all_labels):
    if lbl < 0:
        continue
    idxs = np.where(all_labels == lbl)[0]
    if len(idxs) < 8:
        continue
    pts = np.asarray(stairs_cloud.points)[idxs]
    # PCA via covariance SVD
    cov = np.cov(pts.T)
    U, S, Vt = np.linalg.svd(cov)
    normal = Vt[-1]  # smallest principal direction = normal of planar patch
    normal_z = abs(normal[2])
    # planarity: smallest singular value relative to sum should be small
    planarity = S[-1] / (S.sum() + 1e-12)
    if normal_z < 0.35 and planarity < 0.2:
        accepted_labels.add(lbl)


# build final labels aligned with stairs_cloud points (keep only accepted clusters)
labels = np.full(len(stairs_cloud.points), -1, dtype=int)
mask_idxs = np.hstack([np.where(all_labels == l)[0] for l in accepted_labels]) if accepted_labels else np.array([], dtype=int)
if mask_idxs.size:
    # re-index accepted clusters 0..N-1
    new_label = 0
    for lbl in sorted(accepted_labels):
        idxs = np.where(all_labels == lbl)[0]
        labels[idxs] = new_label
        new_label += 1

max_label = labels.max()
print(f"Accepted {len(accepted_labels)} planar vertical cluster(s)")

# --- visualize clusters ---
if len(stairs_cloud.points) > 0:
    # import numpy as np
    # import open3d as o3d

    # deterministic random colors for labels 0..max_label
    rng = np.random.RandomState(42)
    label_colors = {lbl: rng.rand(3) for lbl in range(max_label + 1)} if max_label >= 0 else {}

    # default/unlabeled color (light gray)
    colors = np.tile(np.array([0.75, 0.75, 0.75]), (len(labels), 1))
    for i, lbl in enumerate(labels):
        if lbl >= 0:
            colors[i] = label_colors[int(lbl)]

    # assign colors to the point cloud and visualize
    stairs_cloud.colors = o3d.utility.Vector3dVector(colors)

    # optional: also draw each cluster with its AABB in a contrasting color
    geoms = [stairs_cloud]
    for lbl in range(max_label + 1):
        idxs = np.where(labels == lbl)[0]
        if idxs.size == 0:
            continue
        cluster = stairs_cloud.select_by_index(idxs)
        aabb = cluster.get_axis_aligned_bounding_box()
        aabb.color = (1.0, 0.0, 0.0)  # red boxes
        geoms.append(aabb)

    o3d.visualization.draw_geometries(geoms)


# -------------------------------
# 5. Sort risers along staircase direction
# -------------------------------
riser_clusters = []
for i in range(max_label + 1):
    cluster_i = stairs_cloud.select_by_index(np.where(labels == i)[0])
    aabb = cluster_i.get_axis_aligned_bounding_box()
    riser_clusters.append({
        "cluster": cluster_i,
        "aabb": aabb,
        "center": aabb.get_center()
    })

# Sort by X or Y depending on staircase orientation
riser_clusters.sort(key=lambda x: x["center"][0])  # replace 0 with the axis along staircase

# -------------------------------
# 6. Infer treads from risers
# -------------------------------
stair_parameters = []
for i in range(len(riser_clusters)-1):
    riser = riser_clusters[i]["aabb"]
    next_riser = riser_clusters[i+1]["aabb"]

    riser_height = riser.get_extent()[2]  # vertical
    tread_depth = next_riser.get_center()[0] - riser.get_center()[0]  # along walking direction
    stair_width = riser.get_extent()[1]  # horizontal

    stair_parameters.append({
        "step": i,
        "riser_height": riser_height,
        "tread_depth": tread_depth,
        "stair_width": stair_width
    })

# -------------------------------
# 7. Report
# -------------------------------
print("Inferred stair parameters:")
for s in stair_parameters:
    print(f"Step {s['step']}: Riser={s['riser_height']:.3f} m, "
          f"Tread={s['tread_depth']:.3f} m, Width={s['stair_width']:.3f} m")

# -------------------------------
# 8. Optional: visualize
# -------------------------------
colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
stairs_cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])
# o3d.visualization.draw_geometries([stairs_cloud])
