from flask import Flask, request, jsonify
import subprocess
import json
import uuid
import os

app = Flask(__name__)

# Load existing function registry or create new one
REGISTRY_PATH = "function_registry.json"

# Ensure registry file exists
if not os.path.exists(REGISTRY_PATH):
    with open(REGISTRY_PATH, "w") as f:
        json.dump({}, f)

# Load functions
with open(REGISTRY_PATH, "r") as f:
    function_registry = json.load(f)

@app.route('/')
def home():
    print("✅ Server connected: Browser accessed root URL")
    return "Serverless Platform is running!"

@app.route('/register', methods=['POST'])
def register_function():
    data = request.json
    function_name = data.get("function_name")
    dockerfile = data.get("dockerfile")  # e.g., 'Dockerfile.greet'

    if not function_name or not dockerfile:
        return jsonify({"error": "function_name and dockerfile are required"}), 400

    image_tag = f"{function_name}-{uuid.uuid4().hex[:6]}"
    dockerfile_path = f"docker_images/{dockerfile}"

    print(f"📦 Building Docker image for {function_name} using {dockerfile_path}")

    result = subprocess.run(
        ["docker", "build", "-f", dockerfile_path, "-t", image_tag, "."],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Docker build failed")
        return jsonify({"error": "Docker build failed", "details": result.stderr}), 500

    function_registry[function_name] = image_tag
    with open(REGISTRY_PATH, "w") as f:
        json.dump(function_registry, f)

    print(f"✅ Function '{function_name}' registered with image '{image_tag}'")
    return jsonify({"message": f"Function '{function_name}' registered", "image_tag": image_tag})


@app.route('/invoke/<function_name>', methods=['GET'])
def invoke_function(function_name):
    image_tag = function_registry.get(function_name)
    if not image_tag:
        return jsonify({"error": f"Function '{function_name}' not found"}), 404

    print(f"🚀 Running function '{function_name}' in Docker container")

    result = subprocess.run(
        ["docker", "run", "--rm", image_tag],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Docker execution failed")
        return jsonify({"error": "Docker run failed", "details": result.stderr}), 500

    print(f"✅ Output from function '{function_name}': {result.stdout.strip()}")
    return jsonify({"output": result.stdout.strip()})

if __name__ == '__main__':
    app.run(debug=True)
