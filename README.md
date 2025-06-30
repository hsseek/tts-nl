# TTS Batch Converter & Sync Tool

Batch convert Korean `.txt` files to TTS audio → auto-skip duplicates, log runs, sync to Android, back up locally, and clean up output folders.

---

## 📂 Project Structure

- `converter.py` — The Python script:
  - Converts each line of each `.txt` file into a separate `.mp3`
  - Skips lines that already exist with nearly identical audio duration
  - Updates the source `.txt` file, leaving only unconverted lines
  - Creates timestamped logs for each run

- `sync_tts.sh` — The Bash script:
  - Activates your Python virtual environment
  - Runs `converter.py`
  - Pushes the generated `.mp3` files to your Android device (`/sdcard/Music/tts/[DD-MM-YYYY]`)
  - Moves `.mp3` and log files to your local backup folder
  - Cleans up empty directories

---

## ⚙️ How to Use

1. **Put your `.txt` files** in the working directory.
2. **Run the bash script:**
   ```bash
   ./sync_tts.sh
