# Missing File Finder

Compare a backup or "updated" copy of a folder against the original, find the files that didn't make it across, and optionally copy them over. Includes a generator for sample data so you can try it safely.

**Short description (for the GitHub "About" field):**
> Python tools to find files missing from a copied folder tree, report them as CSV, and optionally copy them across. Includes a sample-data generator for testing.

## Contents

| File | Purpose |
|---|---|
| `FindMissingFiles.py` | Compares two folder trees, reports missing files, and offers to copy them. |
| `GenerateSampleFolders.py` | Builds a random test folder tree and an incomplete copy of it. |

## Requirements

- Python 3.6 or newer
- No third-party packages (standard library only)

## FindMissingFiles.py

Walks every folder in the original directory and checks whether each file exists at the same relative path in the updated directory.

### What it does

1. Checks that both folders exist.
2. Prints a CSV of every missing file (`folder`, `missing_file`) to the console.
3. Saves two reports:
   - `missing_files.csv`: one row per missing file.
   - `missing_summary.csv`: one row per folder that has missing files, with these columns:
     - `folder`
     - `original_file_count`
     - `files_present`
     - `percent_present`
     - `missing_files` (names separated by `; `)
4. Asks whether to copy the missing files across. Answer `yes` or `y` to copy; anything else copies nothing.

When copying, files keep their relative folder path, any missing folders are created, and original timestamps are preserved. Existing files are never overwritten. If a file can't be copied, the script carries on and lists the failures at the end.

### Usage

Set the folder paths at the bottom of the script:

```python
THUMBDRIVE_DIR = "thumbdrive_original"
UPDATED_DIR = "thumbdrive_updated"
```

Then run it from a terminal or command prompt:

```
python FindMissingFiles.py
```

### Notes and limitations

- A file counts as present if a file with the same name exists at the same relative path. Contents, size, and modified dates are **not** compared, so a changed or corrupted file will not be flagged.
- It only looks for files missing from the updated folder. Extra files that exist only in the updated folder are ignored.
- In the summary, counts and percentages cover the files directly inside each folder. Subfolders get their own rows.
- The prompt copies files into the updated folder, so try it on test data first (see below).

## GenerateSampleFolders.py

Creates test data for `FindMissingFiles.py`.

### What it does

1. Builds `thumbdrive_original` as a three-level folder tree. Each level has three subfolders, giving 39 folders in total. Each folder holds three `.txt` files with random names and random word content.
2. Builds `thumbdrive_updated` with the same folder structure but randomly incomplete contents. Each folder with files is assigned one of three outcomes, with equal probability:
   - **No copy:** the folder exists but is empty.
   - **Partial copy:** a random subset of its files is copied.
   - **Full copy:** all of its files are copied.

### Usage

```
python GenerateSampleFolders.py
```

> **Warning:** it deletes and recreates `thumbdrive_original` and `thumbdrive_updated` in the current directory each time it runs. Don't run it in a folder where those names hold real data.

## Quick start

```
python GenerateSampleFolders.py
python FindMissingFiles.py
```

Run both from the same folder. You'll get the two CSV reports and a prompt to copy the missing files into `thumbdrive_updated`. Answering `yes` and running `FindMissingFiles.py` again should report no missing files.
