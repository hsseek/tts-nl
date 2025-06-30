from datetime import datetime
import edge_tts
import asyncio
import re
import shutil
import argparse
from glob import glob
from pathlib import Path
from collections import defaultdict
from mutagen.mp3 import MP3
import uuid

# === CONFIG ===
voice_name = "ko-KR-SunHiNeural"
rate = "+50%"
punctuation_pattern = re.compile(r"[.,;:!?]")

used_names = defaultdict(int)

def get_duration(file_path: Path) -> float:
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception:
        return -1.0

def get_base_filename(line: str) -> str:
    base = punctuation_pattern.split(line, maxsplit=1)[0]
    base = re.sub(r"\s+", "_", base.strip()) or "line"
    return base[:20]  # Limit to 20 characters

def get_available_filename(base_dir: Path, base: str) -> Path:
    count = 1
    while True:
        suffix = f"_{count}" if count > 1 else ""
        filename = f"{base}{suffix}.mp3"
        full_path = base_dir / filename
        if not full_path.exists():
            return full_path
        count += 1

async def convert_file(txt_path: Path, force: bool):
    output_dir = Path(txt_path.stem)

    if force and output_dir.exists():
        print(f"🧹 Removing and regenerating folder: {output_dir}/")
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = output_dir / f"log-{txt_path.stem}-{timestamp}.txt"
    used_names.clear()

    with txt_path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print(f"⚠️  '{txt_path.name}' is empty or only contains blank lines.")
        return

    conversion_count = 0
    remaining_lines = list(lines)

    with log_file.open("a", encoding="utf-8") as log:
        for line in lines:
            base = get_base_filename(line)
            final_path = get_available_filename(output_dir, base)

            # Step 1: Generate to temporary file
            temp_filename = f"{uuid.uuid4().hex}.mp3"
            temp_path = output_dir / temp_filename
            communicate = edge_tts.Communicate(
                text=line,
                voice=voice_name,
                rate=rate
            )
            await communicate.save(str(temp_path))

            new_duration = get_duration(temp_path)

            # Step 2: Check for existing file with same base name
            possible_existing = output_dir / f"{base}.mp3"
            if possible_existing.exists():
                existing_duration = get_duration(possible_existing)
                if abs(existing_duration - new_duration) < 2.0:  # Smaller than the threshold duration
                    print(f"⏭️  Skipping duplicate (duration match): {possible_existing.name}")
                    temp_path.unlink()  # Delete temp
                    remaining_lines.remove(line)
                    continue

            # Step 3: Move to final name
            temp_path.rename(final_path)
            conversion_count += 1
            print(f"💬 Created: {final_path}")
            log.write(f"{final_path.name} <- {line}\n")
            remaining_lines.remove(line)

    with txt_path.open("w", encoding="utf-8") as f:
        for line in remaining_lines:
            f.write(line + "\n")
    print(f"✅ Saved {conversion_count} files.")

async def main():
    parser = argparse.ArgumentParser(description="Convert .txt files to Korean TTS audio.")
    parser.add_argument("--force", action="store_true", help="Force regenerate folders (delete existing ones)")
    args = parser.parse_args()

    txt_files = glob("*.txt")
    if not txt_files:
        print("📂 No .txt files found in the current directory.")
        return

    for txt_file in txt_files:
        print(f"\n📄 Processing: {txt_file}")
        await convert_file(Path(txt_file), args.force)

asyncio.run(main())
