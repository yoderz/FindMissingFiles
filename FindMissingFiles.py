import os
import csv
import sys
import shutil


def copy_missing_files(thumbdrive_path, updated_path, missing_entries):
    """Copy each missing file from the original folder into the updated folder,
    preserving its relative folder path and creating folders as needed."""
    copied = 0
    failed = []

    for folder, file_name in missing_entries:
        src_dir = thumbdrive_path if folder == "." else os.path.join(thumbdrive_path, folder)
        dst_dir = updated_path if folder == "." else os.path.join(updated_path, folder)
        src_file = os.path.join(src_dir, file_name)
        dst_file = os.path.join(dst_dir, file_name)

        try:
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(src_file, dst_file)  # copy2 keeps timestamps
            copied += 1
        except Exception as e:
            failed.append((src_file, str(e)))

    print(f"\nCopied {copied} of {len(missing_entries)} missing files.")
    if failed:
        print(f"{len(failed)} file(s) could not be copied:")
        for path, err in failed:
            print(f"  {path}: {err}")


def compare_folders(
    thumbdrive_path,
    updated_path,
    output_csv="missing_files.csv",
    summary_csv="missing_summary.csv",
):
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

    missing_entries = []   # (folder, file_name), one per missing file
    folder_stats = {}      # folder -> {"total": int, "missing": [names]}

    # Walk through all directories and files on the thumbdrive
    for root, dirs, files in os.walk(thumbdrive_path):
        # Determine relative folder path compared to root
        rel_folder = os.path.relpath(root, thumbdrive_path)
        folder_display = "." if rel_folder == "." else rel_folder

        # Calculate expected directory path in updated version
        target_dir = os.path.join(updated_path, rel_folder) if rel_folder != "." else updated_path

        stats = folder_stats.setdefault(folder_display, {"total": 0, "missing": []})

        for file_name in files:
            stats["total"] += 1
            target_file_path = os.path.join(target_dir, file_name)

            # Check if file exists in the updated folder structure
            if not os.path.exists(target_file_path):
                missing_entries.append((folder_display, file_name))
                stats["missing"].append(file_name)

    # Print CSV output to standard output (one missing file per line)
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

    # Summary CSV: one row per folder that has at least one missing file
    if summary_csv:
        with open(summary_csv, mode="w", newline="", encoding="utf-8") as f:
            summary_writer = csv.writer(f)
            summary_writer.writerow([
                "folder",
                "original_file_count",
                "files_present",
                "percent_present",
                "missing_files",
            ])
            for folder, stats in folder_stats.items():
                if not stats["missing"]:
                    continue
                total = stats["total"]
                present = total - len(stats["missing"])
                percent = (present / total * 100) if total else 0.0
                summary_writer.writerow([
                    folder,
                    total,
                    present,
                    f"{percent:.1f}%",
                    "; ".join(sorted(stats["missing"])),
                ])
        print(f"[+] Saved summary to {summary_csv}", file=sys.stderr)

    # Offer to copy the missing files across
    if not missing_entries:
        print("\nNo missing files. Nothing to copy.")
        return

    answer = input(
        f"\n{len(missing_entries)} file(s) are missing from the updated folder. "
        "Copy them across now? (yes/no): "
    ).strip().lower()

    if answer in ("y", "yes"):
        copy_missing_files(thumbdrive_path, updated_path, missing_entries)
    else:
        print("No files copied.")


if __name__ == "__main__":
    # Replace these paths with your actual folder paths
    THUMBDRIVE_DIR = "thumbdrive_original"
    UPDATED_DIR = "thumbdrive_updated"

    compare_folders(THUMBDRIVE_DIR, UPDATED_DIR)
