import os
import csv
import sys

def compare_folders(thumbdrive_path, updated_path, output_csv="missing_files.csv"):
    thumbdrive_path = os.path.abspath(thumbdrive_path)
    updated_path = os.path.abspath(updated_path)

    if not os.path.exists(thumbdrive_path):
        print(f"Thumbdrive path does not exist: {thumbdrive_path}")
        return
    if not os.path.exists(updated_path):
        print(f"Updated path does not exist: {updated_path}")
        return
    print(f"Thumbdrive path exists: {thumbdrive_path}")
    print(f"Updated path exists: {updated_path}")

    missing_entries = []

    # Walk through all directories and files on the thumbdrive
    for root, dirs, files in os.walk(thumbdrive_path):
        # Determine relative folder path compared to root
        rel_folder = os.path.relpath(root, thumbdrive_path)
        
        # Calculate expected directory path in updated version
        target_dir = os.path.join(updated_path, rel_folder) if rel_folder != "." else updated_path

        for file_name in files:
            target_file_path = os.path.join(target_dir, file_name)
            
            # Check if file exists in the updated folder structure
            if not os.path.exists(target_file_path):
                folder_display = "." if rel_folder == "." else rel_folder
                print(f"Missing file: {target_file_path}")
                missing_entries.append((folder_display, file_name))
            else:
                print(f"File exists: {target_file_path}")

    # Print CSV output to standard output
    writer = csv.writer(sys.stdout)
    writer.writerow(["folder", "missing_file"])
    for folder, file_name in missing_entries:
        writer.writerow([folder, file_name])

    # Optional: Save to CSV file
    if output_csv:
        with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
            file_writer = csv.writer(f)
            file_writer.writerow(["folder", "missing_file"])
            file_writer.writerows(missing_entries)
        print(f"\n[+] Saved results to {output_csv}", file=sys.stderr)


if __name__ == "__main__":
    # Replace these paths with your actual folder paths
    THUMBDRIVE_DIR = "thumbdrive_original"
    UPDATED_DIR = "thumbdrive_updated"

    compare_folders(THUMBDRIVE_DIR, UPDATED_DIR)