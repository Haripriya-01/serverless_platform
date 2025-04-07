# File: docker_executor.py

import subprocess

# Map function names to Docker image names
IMAGE_MAP = {
    "hello": "hello-image",
    "greet": "greet-image",
    "add": "add-image"
}

def run_function_in_docker(func_name):
    image_name = IMAGE_MAP.get(func_name)
    if not image_name:
        return f"Error: No image found for function '{func_name}'"

    try:
        result = subprocess.run(
            ["docker", "run", "--rm", image_name],
            capture_output=True,
            text=True,
            timeout=5  # 5 second timeout
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error running function '{func_name}': {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return f"Error: Function '{func_name}' execution timed out!"
