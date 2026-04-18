# talking to the operating system
import os

def rename_files(folder_path, prefix="", suffix="", file_type=None):
    if not os.path.exists(folder_path):
        print("Folder does not exist.")
        return

    files = os.listdir(folder_path)

    count = 1

    for filename in files:
        old_path = os.path.join(folder_path, filename)

        # skip folders
        if not os.path.isfile(old_path):
            continue

        # filter by file type
        if file_type and not filename.endswith(file_type):
            continue

        name, ext = os.path.splitext(filename)

        new_name = f"{prefix}{count}{suffix}{ext}"
        new_path = os.path.join(folder_path, new_name)

        os.rename(old_path, new_path)

        print(f"{filename} → {new_name}")
        count += 1


def main():
    folder = input("Enter folder path: ").strip()
    prefix = input("Prefix (optional): ").strip()
    suffix = input("Suffix (optional): ").strip()
    file_type = input("File type (e.g. .jpg) or press Enter: ").strip()

    if file_type == "":
        file_type = None

    rename_files(folder, prefix, suffix, file_type)


if __name__ == "__main__":
    main()