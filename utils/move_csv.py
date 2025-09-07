import shutil
import os

def move_csv(file_path, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)  
    file_name = os.path.basename(file_path)
    dest_path = os.path.join(dest_dir, file_name)
    shutil.move(file_path, dest_path)
    return dest_path