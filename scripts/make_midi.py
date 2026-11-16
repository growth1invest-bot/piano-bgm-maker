"""Lyrical original piano composition for FreePats Upright Piano KW.
A continuous 8-bar tune and answer, with legato playing and connected harmony.
"""
import random
from pathlib import Path
import mido

T=480
B=4*T
random.seed(27)
r=random.Random(2705)
out=Path("output")
out.mkdir(exist_ok=True)
midi=mido.MidiFile(ticks_per_beat=T)
tr=mido.MidiTrack()
midi.tracks.append(tr)
tr.append(mido.Message("program_change",program=0,channel=0,time=0))
ev=[]
def add(at,priority,msg):
    ev.append((max(0,int(round(at))),priority,msg))
def cc(at,num,val):
    add(at,1,mido.Message("control_change",channel=0,control=num,value=val,time=0))
def tone(at,p,dur,vel):
    st=at+r.uniform(-0.012,0.012)*T
    end=at+dur*T
    add(st,2,mido.Message("note_on",channel=0,note=p,velocity=max(15,min(110,int(vel))),time=0))
    add(end,0,mido.Message("note_off",channel=0,note=p,velocity=0,time=0))
# root, voicing (all notes on and close to their chord)
harmony=[
 (48,[55,60,64,67,71]), # Cmaj9
 (45,[52,57,60,64,67]), # Am7
 (53,[57,60,65,69,72]), # Fmaj7
 (55,[59,62,65,69,74]), # G9
 (52,[55,59,64,67,71]), # Em7
 (45,[52,57,60,64,69]), # Am
 (50,[57,60,65,69,72]), # Dm7
 (55,[59,62,65,69,74]), # G9
]
# Two 8-bar connected melodies, written note by note (pitch, onset, duration).
# The last tone in a bar often approaches the first tone of the next.
theme=[
 [(76,0,1.5),(74,1.5,.9),(72,2.4,1.6)],
 [(72,0,1.15),(69,1.15,1.1),(72,2.25,1.75)],
 [(72,0,1.5),(69,1.5,.8),(65,2.3,1.7)],
 [(67,0,1.0),(69,1,1),(71,2,2)],
 [(71,0,1.5),(67,1.5,1.1),(64,2.6,1.4)],
 [(69,0,1.0),(72,1,1.5),(76,2.5,1.5)],
 [(77,0,1.5),(76,1.5,1),(72,2.5,1.5)],
 [(74,0,1.1),(71,1.1,1.1),(72,2.2,1.8)],
]
answer=[
 [(72,0,1.15),(76,1.15,1.35),(79,2.5,1.5)],
 [(76,0,1.4),(72,1.4,1.0),(69,2.4,1.6)],
 [(69,0,1.0),(72,1.0,1.2),(77,2.2,1.8)],
 [(74,0,1.0),(71,1.0,1.0),(69,2.0,2.0)],
 [(67,0,1.5),(71,1.5,1.0),(76,2.5,1.5)],
 [(76,0,1.3),(72,1.3,.9),(69,2.2,1.8)],
 [(69,0,1.1),(65,1.1,1.1),(69,2.2,1.8)],
 [(71,0,1.25),(74,1.25,1.0),(72,2.25,1.75)],
]
# intro 4 bars; tune+answer twice, contrasting 16 bars, reprise 16 bars,
# and 4-bar coda = 72 bars total.
sections=[("intro",4),("theme",16),("theme_var",16),("bridge",16),("reprise",16),("coda",4)]
bar=0
for section,length in sections:
    for n in range(length):
        start=bar*B
        h=bar%8
        root, chord=harmony[h]
        localgroup=n//8
        wave=1-abs((n%8)-3.5)/3.5
        dynamic={"intro":.66,"theme":.88,"theme_var":.92,"bridge":.95,"reprise":.84,"coda":.65}[section]
        dynamic*=.94+.13*wave
        # 78 BPM with a tiny phrase-end relaxation only.
        speed=76 if section in ("intro","coda") else 80 if section=="bridge" else 78
        if n%8==7 and section not in ("intro","coda"):
            speed-=2
        add(start,1,mido.MetaMessage("set_tempo",tempo=mido.bpm2tempo(speed),time=0))
        # Accompaniment v4: a single quiet, sustained chord per bar.
        # No off-beat plucks, repeated short bass notes or eighth-note ostinato.
        # Keep the accompaniment below the right-hand melody to prevent
        # competing attacks and accidental same-key note-offs.
        cc(start if bar else 0,64,0)
        cc(start+36,64,86)
        left_voicing = {
            48: [48,55,60], 45: [45,52,57], 53: [41,53,60],
            55: [43,55,59], 52: [40,52,59], 50: [38,50,57],
        }[root]
        # Slightly stagger the three fingers, mimicking a gentle rolled chord.
        # Nearly full-bar holds preserve a bed of sound until harmony changes.
        for ix, pitch in enumerate(left_voicing):
            tone(start+ix*26, pitch, 3.88-ix*.04,
                 (36 + (3 if ix==0 else 0) + r.randint(-2,2))*dynamic)
        if section=="intro":
            melody=[(72,.5,2.5)] if n%2==0 else [(69,.3,1.9),(67,2.2,1.6)]
        elif section=="coda":
            melody=[[(76,0,1.7),(72,1.7,2.3)],
                    [(69,0,2.0),(72,2,2.0)],
                    [(71,0,1.6),(72,1.6,2.4)],
                    [(72,0,3.7)]][n]
        else:
            melody=(theme if (n//8)%2==0 else answer)[n%8]
            if section=="bridge":
                # A softer, more open register before returning to the theme.
                melody=[(p-12 if p>=76 else p,b,d) for p,b,d in melody]
            elif section=="theme_var":
                # An ornament on an existing melodic note, not a new melody.
                p0,b0,d0=melody[0]
                if d0>1.2 and n%4==2:
                    melody=[(p0,b0,d0*.65),(p0+2,b0+d0*.65,d0*.35)]+melody[1:]
        for k,(pitch,beat,dur) in enumerate(melody):
            velocity=(62+5*(k==0)+r.randint(-4,4))*dynamic
            # Slight overlap between melodic notes makes the line legato.
            hold=dur+(0.10 if k<len(melody)-1 else 0.04)
            tone(start+beat*T,pitch,hold,velocity)
        bar+=1
# A final tonic instead of a hard ending
end=bar*B
cc(end-25,64,0)
cc(end+80,64,78)
for ix,p in enumerate([48,55,60,64,72,76]):
    tone(end+ix*24,p,3.8,46+2*ix)
cc(end+4.25*T,64,0)
events=sorted(ev,key=lambda x:(x[0],x[1]))
last=0
for tick,_,message in events:
    tr.append(message.copy(time=tick-last))
    last=tick
tr.append(mido.MetaMessage("end_of_track",time=3*T))
name=out/"Upright_KW_Original_Piano.mid"
midi.save(name)
print(f"Generated {name}: {bar} bars, {len(ev)} events")
