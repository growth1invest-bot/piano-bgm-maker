"""Original gentle piano instrumental. Standard MIDI via mido."""
import random
from pathlib import Path
import mido

rng = random.Random(20261115)
out=Path('output');out.mkdir(exist_ok=True)
mid=mido.MidiFile(ticks_per_beat=480)
track=mido.MidiTrack();mid.tracks.append(track)
track.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(84),time=0))
track.append(mido.Message('program_change',program=0,time=0))
chords=[
([48,55,60,64,71],[64,67,72,76]),
([45,52,57,60,64],[64,69,72,76]),
([53,60,65,69,72],[65,69,72,76]),
([55,62,65,69,74],[62,65,69,74]),
([52,59,64,67,71],[64,67,71,76]),
([45,52,57,60,64],[60,64,69,72]),
([50,57,60,65,69],[62,65,69,74]),
([55,62,65,69,71],[62,67,71,74]),
]
notes=[]
for bar in range(96):
    chord, tones=chords[bar%len(chords)]
    base=bar*4*480
    for beat, pitch in zip([0,1.45,2.25,3.2],[chord[0],chord[2],chord[1],chord[3]]):
        start=base+round((beat+rng.uniform(-.025,.025))*480)
        notes.append((max(0,start),True,pitch,rng.randint(44,64)))
        notes.append((start+round(rng.uniform(.75,1.15)*480),False,pitch,0))
    if bar%4==0:
        picks=[(0.15,tones[0],1.25),(1.3,tones[2],.8),(2.8,tones[1],.95)]
    elif bar%4==1:
        picks=[(.5,tones[1],1.0),(2.2,tones[3],.75)]
    elif bar%4==2:
        picks=[(.2,tones[2],1.5),(2.0,tones[0],.9),(3.25,tones[1],.55)]
    else:
        picks=[(.1,tones[1],1.5),(2.7,tones[0],1.1)]
    for b,p,d in picks:
        st=base+round((b+rng.uniform(-.06,.06))*480)
        notes.append((max(0,st),True,p,rng.randint(47,74)))
        notes.append((st+int(d*480),False,p,0))
notes.sort(key=lambda e:(e[0],e[1]))
prev=0
for tick,on,p,vel in notes:
    track.append(mido.Message('note_on' if on else 'note_off',note=p,velocity=vel,time=tick-prev))
    prev=tick
track.append(mido.MetaMessage('end_of_track',time=1))
mid.save(out/'Upright_KW_Original_Piano.mid')
print(out/'Upright_KW_Original_Piano.mid')
