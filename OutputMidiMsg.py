from mido import MidiFile
import sys

midi = MidiFile("files/马勒第六.mid")

with open('files/MidiMessage.txt', 'w', encoding='utf8') as f:
    sys.stdout = f
    track_cnt = 0
    for track in midi.tracks:
        print(f"Track {track_cnt}, name: {track.name}")
        for msg in track:
            print(msg)
        track_cnt += 1
        print("")

with open('files/MidiMessageMerged.txt', 'w', encoding='utf8') as f:
    sys.stdout = f
    for msg in midi.merged_track:
        print(msg)