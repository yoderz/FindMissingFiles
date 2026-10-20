import os
import random
import shutil
import string

ENGLISH_WORDS = [
    "apple", "banana", "cherry", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
    "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray"
]

def generate_random_filename():
    length = random.randint(6, 8)
    name = "".join(random.choices(ENGLISH_WORDS, k=length))
    return f"{name}.txt"

def generate_random_file_content():
    word_count = random.randint(10, 30)
    return " ".join(random.choices(ENGLISH_WORDS, k=word_count))

def create_directory_tree(current_path, depth=1, max_depth=3):
    if depth > max_depth:
        return

    for i in range(1, 4):
        dir_name = f"folder_level{depth}_{i}"
        dir_path = os.path.join(current_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        for _ in range(3):
            file_name = generate_random_filename()
            file_path = os.path.join(dir_path, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(generate_random_file_content())

        create_directory_tree(dir_path, depth=depth + 1, max_depth=max_depth)


def create_partial_copy(source_root, target_root):
    """
    Replicates the full folder structure to target_root, but applies three
    modes when copying files within each directory:
    - no_copy: empty folder (0 files copied)
    - partial_copy: subset of files copied
    - full_copy: all files copied
    """
    for root, dirs, files in os.walk(source_root):
        rel_path = os.path.relpath(root, source_root)
        
        target_dir = target_root if rel_path == "." else os.path.join(target_root, rel_path)
        
        # Always create the folder structure
        os.makedirs(target_dir, exist_ok=True)

        if not files:
            continue

        # Randomly choose file copying behavior for this folder
        choice = random.choices(["no_copy", "partial_copy", "full_copy"], weights=[1, 1, 1])[0]

        if choice == "no_copy":
            # Folder is created, but no files are copied inside
            pass

        elif choice == "partial_copy":
            # Copy a random subset of files (e.g., 1 out of N files)
            num_to_copy = random.randint(1, max(1, len(files) - 1))
            copied_files = random.sample(files, k=num_to_copy)
            for f in copied_files:
                shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))

        elif choice == "full_copy":
            # Copy all files
            for f in files:
                shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))


if __name__ == "__main__":
    ORIGINAL_DIR = "thumbdrive_original"
    UPDATED_DIR = "thumbdrive_updated"

    # Clean up prior test runs
    for path in [ORIGINAL_DIR, UPDATED_DIR]:
        if os.path.exists(path):
            shutil.rmtree(path)

    print("[+] Generating original directory tree and files...")
    create_directory_tree(ORIGINAL_DIR, depth=1, max_depth=3)

    print("[+] Replicating full folder structure with missing files...")
    create_partial_copy(ORIGINAL_DIR, UPDATED_DIR)

    print("[✓] Done! All folder paths exist in 'thumbdrive_updated', with randomized file gaps.")