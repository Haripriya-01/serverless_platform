from flask import Flask, request, jsonify, render_template
import os
import json
import subprocess

app = Flask(__name__)

# Ensure functions directory and registry file exist
os.makedirs("functions", exist_ok=True)
if not os.path.exists("registry.json"):
    with open("registry.json", "w") as f:
        json.dump({}, f)

@app.route("/")
def index():
    with open("registry.json", "r") as f:
        functions = json.load(f)
    return render_template("index.html", functions=functions)

@app.route("/register", methods=["POST"])
def register_function():
    uploaded_file = request.files["file"]
    if not uploaded_file:
        return "No file uploaded", 400

    filename = uploaded_file.filename
    save_path = os.path.join("functions", filename)
    uploaded_file.save(save_path)

    function_name = filename  # Using filename as the function name
    docker_tag = function_name.replace(".py", "") + "-function"

    # Add to registry
    with open("registry.json", "r") as f:
        registry = json.load(f)

    registry[function_name] = docker_tag

    with open("registry.json", "w") as f:
        json.dump(registry, f)

    return f"Function '{function_name}' registered successfully."

@app.route("/invoke/<name>", methods=["POST"])
def invoke_function(name):
    with open("registry.json", "r") as f:
        registry = json.load(f)

    if name not in registry:
        return f"Function {name} not found in registry.", 404

    docker_image = registry[name]

    try:
        result = subprocess.run(
            ["docker", "run", docker_image],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20
        )
        output = result.stdout.decode() + result.stderr.decode()
        return f"<pre>{output}</pre>"
    except subprocess.TimeoutExpired:
        return "Execution timed out", 500
    except Exception as e:
        return f"Error invoking Docker: {str(e)}", 500

if __name__ == "__main__":
    print("Server is running at http://127.0.0.1:5000")
    app.run(debug=True)
