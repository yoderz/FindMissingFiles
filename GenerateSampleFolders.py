import os
import random
import shutil
import string

# Sample list of words to populate dummy text files
ENGLISH_WORDS = [
    "apple", "banana", "cherry", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
    "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray"
]

def generate_random_filename():
    """Generates a random filename with 6-8 letters and .txt extension."""
    length = random.randint(6, 8)
    name = "".join(random.choices(ENGLISH_WORDS, k=length))
    return f"{name}.txt"

def generate_random_file_content():
    """Generates 10-30 random English words for text content."""
    word_count = random.randint(10, 30)
    return " ".join(random.choices(ENGLISH_WORDS, k=word_count))

def create_directory_tree(current_path, depth=1, max_depth=3):
    """
    Recursively creates 3 folders at each level up to max_depth,
    and puts 3 random text files in every folder created.
    """
    if depth > max_depth:
        return

    for i in range(1, 4):
        dir_name = f"folder_level{depth}_{i}"
        dir_path = os.path.join(current_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        # Create 3 random text files in this folder
        for _ in range(3):
            file_name = generate_random_filename()
            file_path = os.path.join(dir_path, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(generate_random_file_content())

        # Recursively build deeper levels
        create_directory_tree(dir_path, depth=depth + 1, max_depth=max_depth)


def create_partial_copy(source_root, target_root):
    """
    Copies source_root to target_root while applying missing/partial logic:
    - ~1/3 of folders are not created at all (no copy)
    - ~1/3 of folders are created as empty or missing files (partial copy)
    - ~1/3 of folders are copied completely (full copy)
    """
    os.makedirs(target_root, exist_ok=True)

    for root, dirs, files in os.walk(source_root):
        rel_path = os.path.relpath(root, source_root)
        
        # Skip processing files at the root level if any, focusing on folders
        if rel_path == ".":
            target_dir = target_root
        else:
            target_dir = os.path.join(target_root, rel_path)

        # Randomly choose outcome for this folder: 0 = No copy, 1 = Partial copy, 2 = Full copy
        choice = random.choices(["no_copy", "partial_copy", "full_copy"], weights=[1, 1, 1])[0]

        if choice == "no_copy":
            # Do not create target folder or copy files
            continue

        elif choice == "partial_copy":
            os.makedirs(target_dir, exist_ok=True)
            # Pick a subset of files to copy (e.g., 1 out of 3 files)
            if files:
                copied_files = random.sample(files, k=random.randint(0, len(files) - 1))
                for f in copied_files:
                    shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))

        elif choice == "full_copy":
            os.makedirs(target_dir, exist_ok=True)
            for f in files:
                shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))


if __name__ == "__main__":
    ORIGINAL_DIR = "thumbdrive_original"
    UPDATED_DIR = "thumbdrive_updated"

    # Clean up prior test runs if they exist
    for path in [ORIGINAL_DIR, UPDATED_DIR]:
        if os.path.exists(path):
            shutil.rmtree(path)

    print("[+] Generating original directory structure...")
    create_directory_tree(ORIGINAL_DIR, depth=1, max_depth=3)

    print("[+] Creating partial/gapped copy...")
    create_partial_copy(ORIGINAL_DIR, UPDATED_DIR)

    print("[✓] Complete! Check 'thumbdrive_original' and 'thumbdrive_updated'.")