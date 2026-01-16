# helpers
import os, json
def save_file(path: str, data: bytes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)

def json_dump(path: str, obj):
    with open(path, "w") as f:
        json.dump(obj, f)
