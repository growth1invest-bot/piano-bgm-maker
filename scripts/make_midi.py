"""Expressive original piano piece for FreePats Upright Piano KW.

No composition knowledge is needed: this program writes a playable MIDI file.
A through-composed 80-bar structure uses distinct sections, hand-shaped phrases,
gentle tempo rubato, varied dynamics and sustain pedal.
"""
from pathlib import Path
import random
import mido

SEED = 20611016
R = random.Random(SEED)
TPB = 480
BPM = 82
BAR = TPB * 4
output = Path("output")
output.mkdir(exist_ok=True)

# The chord roots, left-hand voicings and right-hand melody palette were
# composed for this piece, rather than chosen from random notes.
progressions = [
    [(48, [55,60,64,67], [64,67,71,72,76]), (45,[52,57,60,64],[64,69,72,76]),
     (53,[57,60,65,69],[65,69,72,77]), (55,[59,62,65,69],[62,65,69,74])],
    [(48,[55,60,64,67],[64,67,71,76]), (52,[55,59,64,67],[64,67,71,76]),
     (45,[52,57,60,64],[64,69,72,76]), (55,[59,62,65,69],[62,65,69,74])],
    [(57,[52,57,60,64],[69,72,76,81]), (53,[57,60,65,69],[69,72,77,81]),
     (50,[57,60,65,69],[65,69,72,77]), (55,[59,62,65,69],[67,71,74,79])],
    [(48,[55,60,64,67],[67,71,72,76]), (45,[52,57,60,64],[64,69,72,76]),
     (50,[57,60,65,69],[65,69,72,77]), (55,[59,62,65,69],[62,67,71,74])],
]
# The sequences below are musical gestures: positions within the chord's
# melody palette, onset in beats, and length in beats.
motifs = [
    [(0,.25,1.05),(2,1.55,.55),(1,2.45,1.2)],
    [(1,.15,.7),(3,1.15,.85),(2,2.35,1.3)],
    [(2,.1,1.35),(1,1.85,.6),(0,2.7,.85)],
    [(3,.15,.95),(2,1.35,.65),(1,2.45,1.1)],
    [(0,.35,.75),(1,1.38,.9),(3,2.65,.9)],
    [(2,.25,.7),(3,1.2,.55),(1,2.05,1.35)],
    [(1,.1,1.4),(0,1.98,.65),(2,3.05,.7)],
    [(2,.1,1.15),(1,1.6,.75),(0,2.65,1.2)],
]

events = []
def event(t, priority, msg):
    events.append((max(0,int(t)),priority,msg))
def note(pitch, at, beats, velocity, channel=0):
    t0=int(at)
    t1=t0+max(90,int(beats*TPB))
    event(t0,2,mido.Message("note_on",channel=channel,note=int(pitch),velocity=max(1,min(115,int(velocity))),time=0))
    event(t1,0,mido.Message("note_off",channel=channel,note=int(pitch),velocity=0,time=0))

# Intro (8), A (16), A varied (16), bridge (16), return (16), coda (8)
sections=[("intro",8,0),("A",16,0),("A2",16,1),("bridge",16,2),("return",16,3),("coda",8,0)]
bar_index=0
for section, count, harmony in sections:
    for local in range(count):
        root, voicing, palette=progressions[harmony][(local//2)%4]
        start=bar_index*BAR
        # Musical breathing: subtle bar-level time changes, not random drift.
        tempo=BPM + (2 if section=="bridge" else -3 if section in ("intro","coda") else 0)
        tempo += (-1 if local%8==7 else 0)
        event(start,1,mido.MetaMessage("set_tempo",tempo=mido.bpm2tempo(tempo),time=0))
        strength={"intro":.66,"A":.84,"A2":.92,"bridge":.94,"return":.83,"coda":.61}[section]
        phrase_swell = 1.0 + .09 * (1-abs((local%8)-3.5)/3.5)
        # Pedal is released at each harmony change, never held indefinitely.
        event(start,1,mido.Message("control_change",channel=0,control=64,value=0,time=0))
        event(start+int(.12*TPB),1,mido.Message("control_change",channel=0,control=64,value=85,time=0))
        event(start+int(3.78*TPB),1,mido.Message("control_change",channel=0,control=64,value=0,time=0))
        # Left hand is sparse in the intro/coda, richer in the central sections.
        beats=[0,1.65,2.55] if section in ("intro","coda") else [0,1.05,2.04,3.12]
        choices=[root,voicing[0],voicing[1],voicing[2]]
        for j,b in enumerate(beats):
            if section=="coda" and local==7 and j>0:
                continue
            pitch=choices[j] if section not in ("bridge","A2") else [root,voicing[1],voicing[0],voicing[3]][j]
            jitter=R.uniform(-.028,.028)*TPB
            vel= (48 + (4 if j==0 else 0) + R.randint(-5,4))*strength*phrase_swell
            note(pitch,start+b*TPB+jitter, .75 if j else 1.45,vel)
        # Distinct melodies over the changing harmony, with conversational pauses.
        motif=motifs[(local + (2 if section=="A2" else 4 if section=="bridge" else 0))%len(motifs)]
        for k,(degree,beat,duration) in enumerate(motif):
            if section=="intro" and local<2 and k==1:
                continue
            if section=="coda" and local>=6 and k>=1:
                continue
            shifted=degree
            if section=="A2" and k==1:
                shifted=(degree+1)%4
            elif section=="bridge" and k==0:
                shifted=(degree+1)%4
            pitch=palette[shifted]
            if section=="return" and local in (6,7,14):
                pitch=max(60,pitch-12)
            jitter=R.uniform(-.045,.045)*TPB
            vel=(61 + (7 if k==0 else -2) + R.randint(-6,6))*strength*phrase_swell
            note(pitch,start+beat*TPB+jitter,duration+R.uniform(-.06,.08),vel)
        bar_index+=1

# Gentle final chord. No cut-off: provide time for the sound to decay.
ending=bar_index*BAR
for pitch in (48,55,60,64,72):
    note(pitch,ending+int(R.uniform(0,.075)*TPB),3.2,45 if pitch<65 else 52)
event(ending+int(3.8*TPB),1,mido.Message("control_change",channel=0,control=64,value=0,time=0))

mid=mido.MidiFile(ticks_per_beat=TPB)
track=mido.MidiTrack()
mid.tracks.append(track)
track.append(mido.Message("program_change",channel=0,program=0,time=0))
previous=0
for tick,priority,msg in sorted(events,key=lambda e:(e[0],e[1])):
    track.append(msg.copy(time=tick-previous))
    previous=tick
track.append(mido.MetaMessage("end_of_track",time=TPB*2))
path=output/"Upright_KW_Original_Piano.mid"
mid.save(path)
print(f"Written {path}; {bar_index} bars; {len(events)} performance events")
