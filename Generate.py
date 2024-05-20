import sys
import mido
from Config import *
from Note import Note
from mido import MidiFile
from Tone import Tone
import Tone
import Enveloper

tones = [Tone.tone_flute, Tone.tone_oboe, Tone.tone_clarinet, Tone.tone_bassoon, Tone.tone_bassoon,
         Tone.tone_horn, Tone.tone_horn, Tone.tone_horn, Tone.tone_horn, Tone.tone_trumpet,
         Tone.tone_trumpet, Tone.tone_tuba, Tone.tone_tuba, Tone.tone_drum, Tone.tone_drum,
         Tone.tone_drum, Tone.tone_drum, Tone.tone_drum, Tone.tone_violin, Tone.tone_violin,
         Tone.tone_viola, Tone.tone_cello, Tone.tone_double_bass]
envs = [Enveloper.env_violin] * 23

tpb = [0]
total_msg_num = [0]
msg_cnt = [0]
tempo_signals = []

def convert(x):
    return int(x / (tpb[0] * 1000000) * sr)

def init_tempo_signals(track0):
    tick_sum = 0
    for msg in track0:
        tick_sum += msg.time
        if msg.is_meta and msg.type == 'set_tempo':
            tempo_signals.append(mido.MetaMessage(type='set_tempo', tempo=msg.tempo, time=tick_sum))
            tick_sum = 0

def insert_tempo_signals(track):
    tick_sum = 0
    idx_ts = 0
    num_ts = len(tempo_signals)
    for i, msg in enumerate(track):
        tick = msg.time
        tick_sum += tick
        tick_ts = tempo_signals[idx_ts].time
        if tick_sum >= tick_ts:
            ts_to_insert = tempo_signals[idx_ts].copy()
            ts_to_insert.time -= tick_sum - tick
            track.insert(i, ts_to_insert)
            msg.time = tick_sum - tick_ts
            tick_sum = 0
            idx_ts += 1
        if idx_ts >= num_ts:
            break

def generate(filename: str, output_filename: str):
    midi = MidiFile(filename)
    audio_len = int(midi.length * sr)
    out = np.zeros(audio_len)
    tpb[0] = midi.ticks_per_beat
    total_msg_num[0] = len(midi.merged_track)

    init_tempo_signals(midi.tracks[0])

    for track_idx, track in enumerate(midi.tracks):
        if track_idx > 0:
            insert_tempo_signals(track)
            # with open(f'files/MsgTest/inserted_track{track_idx}.txt', 'w', encoding='utf8') as f:
            #     sys.stdout = f
            #     for msg in track:
            #         print(msg)
        generate_single_track(out, track, tones[track_idx], Enveloper.env_common)

    # generate_single_track(out, midi.merged_track, Tone.tone_violin, Enveloper.env_common)

    max_amp = max(np.abs(out[:]))
    out = out / max_amp * 30000

    testfile = wave.open(output_filename, 'w')
    testfile.setnchannels(1)
    testfile.setframerate(sr)
    testfile.setnframes(out.size)
    testfile.setsampwidth(2)
    testfile.writeframes(out.astype(np.int16))
    print("\nGenerate " + filename + " to file " + output_filename)

def generate_single_track(out, track, tone, env):
    channel_velo = [128] * 32
    channel_breath = [128] * 32

    tempo = 0
    time_cur = int(0)  # 单位：1/tpb 微秒
    note_list = [[None] * 128 for _ in range(32)]  # 当前每个不同音高的音符列表
    note_halt = [[False] * 128 for _ in range(32)]  # 在踏板期间被停止的音符，需在踏板结束时结算
    pedal_on = [False] * 32

    for msg in track:
        ticks = msg.time
        time_cur += ticks * tempo
        if not msg.is_meta:
            channel = msg.channel
            if msg.type == 'note_on' or msg.type == 'note_off':
                pitch = msg.note
                note_prev = note_list[channel][pitch]
                if msg.type == 'note_off':
                    msg.velocity = 0
                velo = msg.velocity * channel_velo[channel]   # * channel_breath[channel] / 128
                if not (pedal_on[channel] and msg.velocity == 0):
                    if note_prev is not None:
                        note_prev.set_end(convert(time_cur))
                        note_wave = note_prev.wave()
                        note_wave_size = note_wave.size
                        if note_prev.pos + note_wave_size > out.size:
                            out = np.append(out, np.zeros(note_prev.pos + note_wave_size - out.size + 10000))
                        out[note_prev.pos:note_prev.pos + note_wave.size] += note_wave

                    note_list[channel][pitch] = Note(convert(time_cur), velo, 0, frequencies[pitch] / 2, tone, env)
                    note_halt[channel][pitch] = False
                else:
                    if note_prev is not None:
                        note_halt[channel][pitch] = True

            if msg.type == 'control_change':
                if msg.control == 7:  # 通道音量
                    channel_velo[channel] = msg.value
                if msg.control == 2:  # 呼吸控制
                    channel_breath[channel] = msg.value
                if msg.control == 64:  # 踏板控制
                    if msg.value == 0:
                        pedal_on[channel] = False
                        for i in range(128):
                            note_remain = note_list[channel][i]
                            if note_remain is not None and note_halt[channel][i]:
                                note_remain.set_end(convert(time_cur))
                                note_wave = note_remain.wave()
                                note_wave_size = note_wave.size
                                if note_remain.pos + note_wave_size > out.size:
                                    out = np.append(out, np.zeros(note_remain.pos + note_wave_size - out.size + 10000))
                                out[note_remain.pos:note_remain.pos + note_wave.size] += note_wave
                                note_list[channel][i] = None
                        note_halt[channel][:] = [False] * 128
                    else:
                        pedal_on[channel] = True
        else:
            if msg.type == 'set_tempo':
                tempo = msg.tempo

        msg_cnt[0] += 1
        print("\r", end="")
        print(f"Total Process: {msg_cnt[0]: >6} / {total_msg_num[0]}", end="")
        sys.stdout.flush()
