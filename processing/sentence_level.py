from pydub import AudioSegment
import json
import os

# Load original audio
audio = AudioSegment.from_wav("record.wav")

# Load phoneme-level JSON
with open("record.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Original transcript split into sentences
sentences = [
    "नमस्कार म नेपालमा बस्छु",
    "मेरो नाम भवेस अधिकारी हो",
    "र मलाई खाना खान मनपर्छ"
]

# Your g2g dictionary (word -> list of phonemes)
g2g_dict = {
    "नमस्कार": ["न", "म", "स्", "का", "र"],
    "म": ["म"],
    "नेपालमा": ["ने", "पा", "ल", "मा"],
    "बस्छु": ["ब", "स्", "छु"],
    "मेरो": ["मे", "रो"],
    "नाम": ["ना", "म"],
    "भवेस": ["भ", "वे", "स"],
    "अधिकारी": ["अ", "धि", "का", "री"],
    "हो": ["हो"],
    "र": ["र"],
    "मलाई": ["म", "ला", "ई"],
    "खाना": ["खा", "ना"],
    "खान": ["खा", "न"],
    "मनपर्छ": ["म", "न", "प", "र्छ"]
}

# Flatten phoneme entries, ignore <unk>
phoneme_entries = [entry for entry in data["tiers"]["words"]["entries"] if entry[2] != "<unk>"]

sentence_timestamps = []
i = 0  # phoneme index

for sentence in sentences:
    words = sentence.split()
    sentence_phonemes = []

    # Collect all phonemes for this sentence
    for word in words:
        phonemes = g2g_dict.get(word)
        if phonemes:
            sentence_phonemes.extend(phonemes)
        else:
            print(f"Warning: Word '{word}' not in dictionary!")

    if not sentence_phonemes:
        continue

    # If we've exhausted phoneme entries, stop processing further sentences
    if i >= len(phoneme_entries):
        print(f"Warning: No more phoneme entries available for sentence '{sentence}' (index {i}). Stopping.")
        break

    start_time = phoneme_entries[i][0]

    # Compute index of last phoneme for this sentence and guard against overflow
    last_index = i + len(sentence_phonemes) - 1
    if last_index >= len(phoneme_entries):
        print(
            f"Warning: Sentence '{sentence}' expects phoneme range up to index {last_index},"
            f" but only {len(phoneme_entries)} phoneme entries available. Using last available entry."
        )
        last_index = len(phoneme_entries) - 1

    end_time = phoneme_entries[last_index][1]

    sentence_timestamps.append({
        "sentence": sentence,
        "start": start_time,
        "end": end_time
    })

    # Move index forward by number of phonemes consumed. Clamp to available length.
    i += len(sentence_phonemes)
    if i > len(phoneme_entries):
        i = len(phoneme_entries)

# Export sentence-level clips
os.makedirs("sentence_clips", exist_ok=True)

for sent_info in sentence_timestamps:
    start_ms = int(sent_info["start"] * 1000)
    end_ms = int(sent_info["end"] * 1000)
    # Clamp clip bounds to audio length and sanity-check
    audio_len_ms = len(audio)
    if start_ms < 0:
        start_ms = 0
    if end_ms > audio_len_ms:
        end_ms = audio_len_ms
    if end_ms <= start_ms:
        print(f"Warning: Invalid clip for sentence '{sent_info['sentence']}' (start {start_ms}, end {end_ms}), skipping.")
        continue

    clip = audio[start_ms:end_ms]
    # Make a filesystem-safe filename by replacing spaces
    safe_name = sent_info['sentence'].replace(' ', '_')
    filename = os.path.join("sentence_clips", f"{safe_name}.wav")
    clip.export(filename, format="wav")
    print(f"Exported {filename}")

# Save sentence-level timestamps JSON
with open("sentence_level_alignment.json", "w", encoding="utf-8") as f:
    json.dump(sentence_timestamps, f, ensure_ascii=False, indent=4)

print("Sentence-level timestamps saved and clips exported.")
