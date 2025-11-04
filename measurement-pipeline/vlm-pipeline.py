import os
import io
import json
import base64
import tempfile
import numpy as np
import open3d as o3d
from PIL import Image
import cv2
import mysql.connector

# Optional: Gemini client
try:
    from google import genai
except ImportError:
    genai = None

# --- MySQL config ---
MYSQL_HOST = "mysql"
MYSQL_USER = "stairuser"
MYSQL_PASSWORD = "stairpass"
MYSQL_DB = "stairs_db"
MYSQL_PORT = 3306

# --- Gemini config ---
GEMINI_API_KEY = "AIzaSyASKeJGq6h9xElLyZmSTOUdxdMqIabWArM"
GEMINI_MODEL = "gemini-2.0-flash-lite"



# ---------- DB helpers ----------
def load_latest_record():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pointclouds ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        raise ValueError("No point cloud found in DB")
    return row


def read_pointcloud_from_bytes(blob: bytes) -> o3d.geometry.PointCloud:
    """Use tempfile because Open3D cannot read from BytesIO."""
    with tempfile.NamedTemporaryFile(suffix=".pcd", delete=False) as tmp:
        tmp.write(blob)
        tmp.flush()
        tmpname = tmp.name
    pc = o3d.io.read_point_cloud(tmpname)
    os.unlink(tmpname)
    return pc


def parse_camera_params(cam_json: str):
    """Parse camera intrinsics and optional extrinsics from JSON string."""
    # print(type(cam_json))
    # print(cam_json)
    if not cam_json:
        return {}
    try:
        cam = json.loads(cam_json)
    except Exception:
        return {}

    print("cx" in cam)
    out = {}

    # Intrinsics
    if "K" in cam:
        K_list = cam["K"]  # keep as list
        out["K_list"] = K_list
        out["fx"], out["fy"], out["cx"], out["cy"] = K_list[0][0], K_list[1][1], K_list[0][2], K_list[1][2]
    elif all(k in cam for k in ("fx", "fy", "cx", "cy")):
        out["fx"], out["fy"], out["cx"], out["cy"] = cam["fx"], cam["fy"], cam["cx"], cam["cy"]
        out["K_list"] = [[cam["fx"], 0, cam["cx"]],
                          [0, cam["fy"], cam["cy"]],
                          [0, 0, 1]]

    # Extrinsics (optional)
    if "extrinsic" in cam:
        out["extrinsic_list"] = cam["extrinsic"]  # keep as list, not ndarray
    
    return out


# ---------- Gemini helpers ----------
def call_gemini_for_segmentation(pil_image: Image.Image):
    """Call Gemini to get bounding boxes and masks (JSON)."""
    if genai is None:
        raise RuntimeError("google-genai not installed")
    print('calling gemini')
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = ("Return JSON list of objects with keys: "
              "'label', 'box_2d' ([ymin,xmin,ymax,xmax] normalized 0-1), "
              "'mask' (optional base64 PNG). Output only JSON.")
    response = client.models.generate_content(model=GEMINI_MODEL, contents=[pil_image, prompt])
    raw = str(response)
    print('raw response:', raw)
    parsed = parse_gemini_response(response)
    print("parsed gemini response:", parsed)
    print("parsed gemini response:", type(parsed))
    # [print() for i in range(10)]
    # Ensure each object has a 'label' and 'box_2d'
    objects = []
    for obj in parsed:
        if "label" in obj and "box_2d" in obj:
            objects.append(obj)


    draw_gemini_boxes(pil_image, objects)

    return objects

def parse_gemini_response(response):
    """
    Extract JSON array from Gemini SDK response.
    Handles triple-backtick formatting.
    """
    # Get the text content of the first candidate/part
    text = response.candidates[0].content.parts[0].text

    # Remove any Markdown triple backticks ```json ... ```
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()
        # optionally remove "json" header
        if text.lower().startswith("json"):
            text = text[4:].strip()

    # Parse JSON
    return json.loads(text)


# ---------- Projection ----------
def project_points_to_image(points_xyz, K, extrinsic=None):
    N = points_xyz.shape[0]
    pts_h = np.hstack([points_xyz, np.ones((N, 1))])
    if extrinsic is not None:
        pts_cam = (extrinsic @ pts_h.T).T
    else:
        pts_cam = pts_h
    xyz = pts_cam[:, :3]
    z = xyz[:, 2]
    z[z == 0] = 1e-6
    u = K[0, 0] * xyz[:, 0] / z + K[0, 2]
    v = K[1, 1] * xyz[:, 1] / z + K[1, 2]
    return np.column_stack([u, v]), z, xyz


def polygon_to_mask(box_2d, img_height, img_width):
    """
    Converts Gemini box_2d (polygon) into a boolean mask of shape (H, W)
    """
    # Convert normalized coordinates [0-1] to pixel coordinates
    pts = np.array([[x * img_width, y * img_height] for y, x in zip(box_2d[::2], box_2d[1::2])], dtype=np.int32)
    mask = np.zeros((img_height, img_width), dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 1)
    return mask.astype(bool)

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import open3d as o3d

def debug_pointcloud_image_mapping(pc, img, camera_params, name="debug"):
    """
    pc: open3d.geometry.PointCloud
    img: PIL.Image
    camera_params: dict with fx, fy, cx, cy, width, height, optional 'extrinsic' 4x4
    name: string prefix for saving outputs
    """
    pts = np.asarray(pc.points)
    print(f"Total points in cloud: {len(pts)}")

    # --- Apply extrinsic if present ---
    if "extrinsic" in camera_params:
        pts_h = np.hstack([pts, np.ones((len(pts),1))])  # Nx4
        pts_cam = (camera_params["extrinsic"] @ pts_h.T).T[:, :3]
    else:
        pts_cam = pts

    # --- Project to image plane ---
    fx, fy, cx, cy = camera_params["fx"], camera_params["fy"], camera_params["cx"], camera_params["cy"]
    z = pts_cam[:, 2]
    z_safe = np.where(z==0, 1e-6, z)
    u = (fx * pts_cam[:, 0] / z_safe + cx).astype(int)
    v = (fy * pts_cam[:, 1] / z_safe + cy).astype(int)

    # --- Filter valid points inside image ---
    valid_mask = (u >= 0) & (u < camera_params["width"]) & \
                 (v >= 0) & (v < camera_params["height"]) & (z > 0)
    u_valid = u[valid_mask]
    v_valid = v[valid_mask]
    pts_valid = pts[valid_mask]

    print(f"Valid projected points: {len(pts_valid)}")

    # --- Create a mask image ---
    img_h, img_w = camera_params["height"], camera_params["width"]
    mask = np.zeros((img_h, img_w), dtype=np.uint8)
    mask[v_valid, u_valid] = 255
    mask_file = f"{name}_projected_mask.png"
    Image.fromarray(mask).save(mask_file)
    print(f"Saved projected mask -> {mask_file}")

    # --- Overlay on original image ---
    img_np = np.array(img.convert("RGB"))
    overlay = img_np.copy()
    overlay[v_valid, u_valid] = [255, 0, 0]  # mark projected points in red
    overlay_file = f"{name}_projected_overlay.png"
    Image.fromarray(overlay).save(overlay_file)
    print(f"Saved overlay -> {overlay_file}")

    # --- Optionally visualize with matplotlib ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(mask, cmap="gray")
    axes[0].set_title("Projected Points Mask")
    axes[1].imshow(overlay)
    axes[1].set_title("Projected Points Overlay")
    plt.show()

    return pts_valid, u_valid, v_valid


from PIL import Image, ImageDraw


def draw_gemini_boxes(img, detections):
    """
    Draw Gemini bounding boxes (rectangles or polygons) on the PIL image.
    """
    draw = ImageDraw.Draw(img)

    for det in detections:
        label = det.get("label", "")
        box = det.get("box_2d", [])
        if not box or len(box) < 4:
            continue

        # Convert normalized coordinates to pixels
        w, h = img.width, img.height
        coords = [(box[i] * w, box[i+1] * h) for i in range(0, len(box)-1, 2)]

        if len(coords) == 2:  # rectangle [x0,y0,x1,y1]
            x0, y0 = coords[0]
            x1, y1 = coords[1]
            # Ensure proper ordering
            x0, x1 = min(x0, x1), max(x0, x1)
            y0, y1 = min(y0, y1), max(y0, y1)
            draw.rectangle([x0, y0, x1, y1], outline="red", width=2)
            draw.text((x0, y0), label, fill="red")
        else:
            # polygon (more than 2 points)
            draw.line(coords + [coords[0]], fill="red", width=2)
            draw.text(coords[0], label, fill="red")
    img.save("pc_with_gemini_boxes_fixed.png")
    return img

# ---------- Main ----------
def main():
    row = load_latest_record()
    name = row["name"]
    print(f"Processing record: {name}")

    # --- Load point cloud ---
    pc = read_pointcloud_from_bytes(row["data"])
    pts = np.asarray(pc.points)
    print(f"Loaded point cloud with {len(pts)} points")

    # --- Save original PCD ---
    pcd_filename = f"{name}.pcd"
    o3d.io.write_point_cloud(pcd_filename, pc)
    pc_down = pc.uniform_down_sample(every_k_points=5)  # keep every 5th point
    pts = np.asarray(pc.points)
    valid_mask = np.isfinite(pts).all(axis=1)
    pts_valid = pts[valid_mask]
    print("Point cloud bounds:")
    print("X:", pts_valid[:,0].min(), pts_valid[:,0].max())
    print("Y:", pts_valid[:,1].min(), pts_valid[:,1].max())
    print("Z:", pts_valid[:,2].min(), pts_valid[:,2].max())

    pc_valid = o3d.geometry.PointCloud()
    pc_valid.points = o3d.utility.Vector3dVector(pts_valid)
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Original Point Cloud")
    vis.add_geometry(pc_valid)

    # Get the view control
    ctr = vis.get_view_control()
    # Set front vector (camera looks from +Z)
    # Set the camera to look along +Z
    ctr.set_front([0, 0, 1])        # camera looks along +Z
    ctr.set_up([0, -1, 0])          # Y-down (typical camera frame)
    ctr.set_lookat(np.mean(pts[valid_mask], axis=0))  # center on the cloud
    ctr.set_zoom(0.8)               # adjust zoom

    vis.run()
    vis.destroy_window()

    # o3d.visualization.draw_geometries([pc_valid])
    print(f"Saved original point cloud to {pcd_filename}")

    # --- Load/save image ---
    if row.get("image_2d"):
        image_bytes = row["image_2d"]
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_filename = f"{name}.png"
        img.save(img_filename)
        print(f"Saved image to {img_filename}")
        # Convert PIL image to OpenCV
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        cv2.imshow("Captured Image", cv_img)
        cv2.waitKey(0)  # Wait for key press
        cv2.destroyAllWindows()
    else:
        print("⚠️ No image found")
        img = None

    # --- Save camera params ---
    camera_params = parse_camera_params(row.get("camera_params"))

    # pts_valid, u_valid, v_valid = debug_pointcloud_image_mapping(pc, img, camera_params, name=row["name"])

    if camera_params:
        cam_filename = f"{name}_camera.json"
        with open(cam_filename, "w") as f:
            json.dump(camera_params, f, indent=2)
        print(f"Saved camera parameters to {cam_filename}")
    else:
        print("⚠️ No camera parameters found")
        # create simple heuristic
        if img is not None:
            w, h = img.size
            fx = fy = max(w, h) * 0.9
            cx, cy = w/2, h/2
            K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
            camera_params = {"K": K, "fx": fx, "fy": fy, "cx": cx, "cy": cy, "extrinsic": None}

    # --- Run Gemini segmentation ---
    if img is not None and GEMINI_API_KEY:
        detections = call_gemini_for_segmentation(img)
        print(f"Gemini returned {len(detections)} detections")
        print(camera_params)

        # --- Prepare camera intrinsics/extrinsics ---
        K = np.array(camera_params["K_list"], dtype=float)
        extrinsic = None
        if "extrinsic_list" in camera_params:
            extrinsic = np.array(camera_params["extrinsic_list"], dtype=float)

        # --- Project point cloud to image ---
        proj_uv, z_cam, cam_xyz = project_points_to_image(pts, K, extrinsic)

        # Filter invalid points (NaN/inf/zero depth)
        valid_points = np.isfinite(proj_uv).all(axis=1) & np.isfinite(z_cam) & (z_cam > 0)
        proj_uv = proj_uv[valid_points]
        cam_xyz = cam_xyz[valid_points]
        pts_valid = pts[valid_points]

        # Round and clip to image bounds
        u = np.clip(np.round(proj_uv[:, 0]).astype(int), 0, img.width - 1)
        v = np.clip(np.round(proj_uv[:, 1]).astype(int), 0, img.height - 1)

        # --- Segment each detected object ---
        segments = []
        for i, det in enumerate(detections, start=1):
            label = det.get("label", f"obj_{i}")
            box = det.get("box_2d")
            if not box or len(box) < 4:
                continue

            # Convert polygon to mask
            mask = polygon_to_mask(box, img.height, img.width)

            # Only keep points inside the mask
            idx = np.where(mask[v, u])[0]
            if len(idx) == 0:
                continue

            # Extract segmented point cloud
            seg_pts = pts_valid[idx]
            seg_pc = o3d.geometry.PointCloud()
            seg_pc.points = o3d.utility.Vector3dVector(seg_pts)
            fname = f"{name}_obj{i}.pcd"
            o3d.io.write_point_cloud(fname, seg_pc)
            print(f"Saved segment '{label}' with {len(seg_pts)} points -> {fname}")

            # Compute centroid distance
            centroid = np.mean(cam_xyz[idx], axis=0)
            distance = float(np.linalg.norm(centroid))
            segments.append({"label": label, "points": len(seg_pts), "distance": distance})
        # save summary
        summary_file = f"{name}_segments.json"
        with open(summary_file, "w") as f:
            json.dump(segments, f, indent=2)
        print(f"Segmentation summary saved to {summary_file}")


if __name__ == "__main__":
    main()


import open3d as o3d
import glob
import numpy as np

# Load all segmented PCDs
pcd_files = sorted(glob.glob("*_obj*.pcd"))
if not pcd_files:
    raise RuntimeError("No segmented PCDs found in the current folder!")

pcd_list = []
colors = [
    [1, 0, 0],    # red
    [0, 1, 0],    # green
    [0, 0, 1],    # blue
    [1, 1, 0],    # yellow
    [1, 0, 1],    # magenta
    [0, 1, 1],    # cyan
    [0.5, 0.5, 0.5]  # gray
]

for i, fname in enumerate(pcd_files):
    pc = o3d.io.read_point_cloud(fname)
    color = colors[i % len(colors)]  # cycle colors if more segments
    pc.paint_uniform_color(color)
    pcd_list.append(pc)

# Visualize all segments together
o3d.visualization.draw_geometries(pcd_list, window_name="Segmented Point Clouds")
