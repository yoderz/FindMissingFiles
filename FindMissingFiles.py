import os
import csv
import sys
import shutil

# Timestamp tolerance in seconds. FAT/exFAT drives (common on thumbdrives)
# store modified times with 2-second resolution, so smaller differences
# are treated as "same time" to avoid false positives.
NEWER_TOLERANCE_SECONDS = 2


def ask_yes_no(question):
    """Ask a yes/no question. Returns True only for 'y' or 'yes'."""
    answer = input(question).strip().lower()
    return answer in ("y", "yes")


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
    newer_summary_csv="newer_summary.csv",
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

    # Ask up front, before scanning, whether to also look for newer files
    check_newer = ask_yes_no(
        "\nAlso check for files that are NEWER in the original folder than in "
        "the updated folder? (yes/no): "
    )

    missing_entries = []   # (folder, file_name), one per missing file
    folder_stats = {}      # folder -> {"total", "missing": [names], "newer": [names]}

    # Walk through all directories and files on the thumbdrive
    for root, dirs, files in os.walk(thumbdrive_path):
        # Determine relative folder path compared to root
        rel_folder = os.path.relpath(root, thumbdrive_path)
        folder_display = "." if rel_folder == "." else rel_folder

        # Calculate expected directory path in updated version
        target_dir = os.path.join(updated_path, rel_folder) if rel_folder != "." else updated_path

        stats = folder_stats.setdefault(
            folder_display, {"total": 0, "missing": [], "newer": []}
        )

        for file_name in files:
            stats["total"] += 1
            source_file_path = os.path.join(root, file_name)
            target_file_path = os.path.join(target_dir, file_name)

            # Check if file exists in the updated folder structure
            if not os.path.exists(target_file_path):
                missing_entries.append((folder_display, file_name))
                stats["missing"].append(file_name)
            elif check_newer:
                # File exists in both: is the original newer than the updated copy?
                try:
                    source_mtime = os.path.getmtime(source_file_path)
                    target_mtime = os.path.getmtime(target_file_path)
                    if source_mtime - target_mtime > NEWER_TOLERANCE_SECONDS:
                        stats["newer"].append(file_name)
                except OSError as e:
                    print(f"Could not compare timestamps for {source_file_path}: {e}",
                          file=sys.stderr)

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

    # Newer-files summary: one row per folder with at least one newer file
    if check_newer and newer_summary_csv:
        newer_total = 0
        with open(newer_summary_csv, mode="w", newline="", encoding="utf-8") as f:
            newer_writer = csv.writer(f)
            newer_writer.writerow([
                "folder",
                "original_file_count",
                "files_present",
                "newer_file_count",
                "percent_newer",
                "newer_files",
            ])
            for folder, stats in folder_stats.items():
                if not stats["newer"]:
                    continue
                total = stats["total"]
                present = total - len(stats["missing"])
                newer_count = len(stats["newer"])
                newer_total += newer_count
                # Percentage of the files present in both folders that are newer
                percent = (newer_count / present * 100) if present else 0.0
                newer_writer.writerow([
                    folder,
                    total,
                    present,
                    newer_count,
                    f"{percent:.1f}%",
                    "; ".join(sorted(stats["newer"])),
                ])
        print(f"[+] Saved newer-files summary to {newer_summary_csv} "
              f"({newer_total} newer file(s))", file=sys.stderr)

    # Offer to copy the missing files across
    if not missing_entries:
        print("\nNo missing files. Nothing to copy.")
        return

    if ask_yes_no(
        f"\n{len(missing_entries)} file(s) are missing from the updated folder. "
        "Copy them across now? (yes/no): "
    ):
        copy_missing_files(thumbdrive_path, updated_path, missing_entries)
    else:
        print("No files copied.")


if __name__ == "__main__":
    # Replace these paths with your actual folder paths
    THUMBDRIVE_DIR = "thumbdrive_original"
    UPDATED_DIR = "thumbdrive_updated"

    compare_folders(THUMBDRIVE_DIR, UPDATED_DIR)
