from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_binary():
    data = request.get_json(force=True)  # parse JSON body
    pointcloud_id = data.get("pointcloud_id")

    if not isinstance(pointcloud_id, int):
        return jsonify({"success": False, "error": "Missing or invalid 'id' (must be integer)"}), 400

    print(f"Received request with id={pointcloud_id}", flush=True)

    result = subprocess.run(
        ["/data/point-cloud-infra/StairwayDetection/build/stair_det", str(pointcloud_id), "/data/point-cloud-infra/StairwayDetection/point-clouds/output.pcd", "mysql", "3306", "stairuser", "stairpass", "stairs_db", "--enable-viewer"],
        capture_output=True, text=True
    )

    print(result.stdout, flush=True)
    print(result.stderr, flush=True)

    return jsonify({
        "success": result.returncode == 0,
        "id": pointcloud_id,
        "stdout": result.stdout,
        "stderr": result.stderr
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
