import json
import os
import shutil

__all__ = ["build_storage"]


def _merge_storage_files(dir_path, single_struct=True):
    result = {}

    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)

        if os.path.isfile(item_path) and item.endswith(".json"):
            try:
                with open(item_path, "r", encoding="utf-8") as f:
                    file_content = json.load(f)
            except Exception as e:
                print(f"Failed to parse file {item_path}: {e}")
                file_content = None

            key = os.path.splitext(item)[0]
            if single_struct:
                result.update(file_content)
            else:
                result[key] = file_content

        elif os.path.isdir(item_path):
            if single_struct:
                result.update(_merge_storage_files(item_path))
            else:
                result[item] = _merge_storage_files(item_path)

    return result


def build_storage(source_dir, output_dir, single_struct=True):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    storages = [
        s for s in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, s))
    ]

    for storage in storages:
        storage_dir = os.path.join(source_dir, storage)
        merged_data = _merge_storage_files(storage_dir, single_struct)
        output_file_path = os.path.join(output_dir, f"{storage}.json")

        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)  # noqa

        # print(f"Хранилище {storage_name} {storage} собрано в файл {output_file_path}")
