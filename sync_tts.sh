#!/bin/bash

# === CONFIG ===
BASE_DIR="/home/sun/PythonScripts/tts_nl"
VENV_ACTIVATE="$BASE_DIR/.venv/bin/activate"
PY_SCRIPT="$BASE_DIR/converter.py"

DATE_STAMP=$(date +"%d-%m-%Y")
DEST_DIR="/sdcard/Music/tts/$DATE_STAMP"  # Android target path with date
BACKUP_DIR="/home/sun/Music/tts"      # Local backup path

# === Step 1: Activate venv and generate TTS ===
echo "🐍 Activating virtual environment..."
source "$VENV_ACTIVATE" || { echo "❌ Failed to activate venv"; exit 1; }

echo "📂 Changing to working directory: $BASE_DIR"
cd "$BASE_DIR" || { echo "❌ Failed to cd to $BASE_DIR"; exit 1; }

echo "▶️ Running TTS generation..."
python "$(basename "$PY_SCRIPT")" --force || { echo "❌ Python script failed"; exit 1; }

# === Step 2: Copy .mp3 to Android ===
echo "🔌 Waiting for device..."
adb wait-for-device || { echo "❌ adb wait-for-device failed"; exit 1; }

echo "📁 Creating target folder on Android: $DEST_DIR"
adb shell "mkdir -p '$DEST_DIR'" || { echo "❌ Failed to create directory on Android"; exit 1; }

echo "📤 Copying .mp3 files to Android..."
mp3_files=($(find . -type f -name '*.mp3'))
copy_count=0

for file in "${mp3_files[@]}"; do
    adb push -a "$file" "$DEST_DIR/" >/dev/null || { echo "❌ Failed to copy $(basename "$file") to Android"; exit 1; }
    ((copy_count++))
done

echo "✅ Copied $copy_count file(s) to Android"

# === Step 3: Move .mp3 and log files to backup ===
echo "📦 Moving .mp3 and log*.txt files to backup: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
move_count=0

while IFS= read -r -d '' file; do
    mv -f "$file" "$BACKUP_DIR/"
    ((move_count++))
done < <(find . -type f \( -name '*.mp3' -o -name 'log*.txt' \) -print0)

echo "✅ Moved $move_count file(s) to backup"

# === Step 4: Clean up empty directories ===
echo "🧹 Removing empty directories..."
find . -type d -empty -delete

echo "🏁 Sync complete."

