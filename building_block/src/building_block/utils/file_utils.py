import os


def resolve_file_dest_path(file_name: str, dest_path: str) -> str:
        if dest_path.endswith(os.sep) or os.path.isdir(dest_path):
            os.makedirs(dest_path, exist_ok=True)
            return os.path.join(dest_path, file_name)

        dest_name = os.path.basename(dest_path)
        if dest_name == file_name or os.path.splitext(dest_name)[1]:
            os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
            return dest_path

        os.makedirs(dest_path, exist_ok=True)
        return os.path.join(dest_path, file_name)
