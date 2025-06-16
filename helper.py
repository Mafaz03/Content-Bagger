import os

def delete_files_with_extensions(root_dir, ext = ".json.xz"):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(ext):
                full_path = os.path.join(root, file)
                print(f"Deleting file: {full_path}")
                os.remove(full_path)