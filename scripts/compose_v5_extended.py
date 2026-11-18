"""Extended original piano composition based on the approved v5 melody.
Four developed movements with composed phrase variants, no random note creation.
"""
from pathlib import Path
import mido
T=480; BAR=4*T
OUT=Path('output');OUT.mkdir(exist_ok=True)
chords=[[48,55,59],[47,55,59],[45,52,60],[43,52,59],
        [41,48,57],[40,48,55],[50,57,60],[43,50,59]]
A=[[(76,1),(79,1),(81,1),(79,1)],[(74,1),(76,1),(79,2)],
[(81,1.5),(79,.5),(76,1),(72,1)],[(74,1),(76,1),(79,2)],
[(81,1),(84,1),(81,1),(79,1)],[(79,1),(76,1),(74,1),(72,1)],
[(77,1),(76,1),(74,2)],[(71,1),(74,1),(72,2)]]
B=[[(79,1.5),(81,.5),(79,1),(76,1)],[(74,1),(79,1),(83,2)],
[(84,1),(81,1),(79,1),(76,1)],[(79,1.5),(76,.5),(74,2)],
[(77,1),(81,1),(84,1),(81,1)],[(79,1.5),(76,.5),(72,2)],
[(74,1),(77,1),(76,1),(74,1)],[(71,1),(74,1),(79,2)]]
A2=[[(76,1),(79,1),(81,.5),(79,.5),(76,1)],[(74,1),(76,1),(79,2)],
[(81,1),(79,1),(76,1),(72,1)],[(74,1),(76,1),(79,2)],
[(81,1.5),(84,.5),(81,1),(79,1)],[(79,1),(76,1),(74,1),(72,1)],
[(77,1.5),(76,.5),(74,2)],[(71,1),(74,1),(72,2)]]
C=[[(72,2),(76,1),(79,1)],[(79,1.5),(83,.5),(79,2)],
[(81,1.5),(84,.5),(81,1),(79,1)],[(76,2),(74,1),(71,1)],
[(72,1),(77,1),(81,2)],[(79,2),(76,1),(72,1)],
[(74,1),(77,1),(76,2)],[(71,1),(74,1),(79,2)]]
END=[[(76,1),(79,1),(81,1),(79,1)],[(74,1),(76,1),(79,2)],
[(81,1.5),(79,.5),(76,2)],[(74,1.5),(76,.5),(79,2)],
[(81,1),(79,1),(76,2)],[(79,1),(76,1),(72,2)],
[(77,1),(76,1),(74,2)],[(71,1),(72,3)]]
# Keep the exact approved v5 themes. Build a longer 4-movement arrangement:
# repetition is organized as musical returns, not short audio loops.
# Every item is an authored 8-bar melodic phrase.
B2=[[(79,1),(81,1),(84,1),(81,1)],
    [(79,1.5),(76,.5),(74,1),(79,1)],
    [(84,2),(81,1),(79,1)],
    [(76,1),(79,1),(76,1),(74,1)],
    [(77,1.5),(81,.5),(84,2)],
    [(81,1),(79,1),(76,2)],
    [(74,1),(77,1),(76,1),(72,1)],
    [(71,1.5),(74,.5),(79,2)]]
C2=[[(72,1),(76,1),(79,2)],
    [(83,1.5),(79,.5),(76,2)],
    [(81,1),(84,1),(81,2)],
    [(76,2),(74,1),(71,1)],
    [(72,1.5),(77,.5),(81,2)],
    [(79,1),(76,1),(72,2)],
    [(74,1),(77,1),(76,2)],
    [(71,1),(74,1),(79,2)]]
sections=[
    # Movement 1: presentation
    ('A',A,75,.88),('B',B,77,.94),('A2',A2,75,.96),
    ('contrast',C,73,.83),('return',A,75,.89),('cadence',END,72,.77),
    # Movement 2: gentle rise, following the original melodic contour
    ('A_recall',A,76,.89),('B_developed',B2,78,.98),
    ('A2_developed',A2,77,.99),('C_warm',C2,74,.90),
    ('B_recall',B,76,.93),('cadence2',END,73,.79),
    # Movement 3: quieter contrasting colors
    ('C_quiet',C,72,.74),('C2_quiet',C2,72,.77),
    ('A_sotto',A,73,.78),('B_quiet',B,74,.82),
    ('C2_return',C2,74,.84),('interlude_end',END,72,.72),
    # Movement 4: reprise and resolved ending
    ('A_return',A,75,.92),('B2_return',B2,77,.98),
    ('A2_return',A2,76,.96),('C_final',C,74,.87),
    ('A_final',A,73,.82),('coda',END,70,.72)
]
m=mido.MidiFile(ticks_per_beat=T);track=mido.MidiTrack();m.tracks.append(track)
track.append(mido.Message('program_change',channel=0,program=0,time=0))
events=[]
def add(t,rank,msg): events.append((int(round(t)),rank,msg))
def note(start,end,pitch,vel):
    assert end>start
    add(start,2,mido.Message('note_on',channel=0,note=pitch,velocity=int(vel)))
    add(end,0,mido.Message('note_off',channel=0,note=pitch,velocity=0))
bar=0
for section,score,bpm,volume in sections:
    for i,line in enumerate(score):
        st=bar*BAR
        add(st,1,mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(bpm-(2 if i==7 else 0))))
        add(max(0,st-24),1,mido.Message('control_change',channel=0,control=64,value=0))
        add(st+100,1,mido.Message('control_change',channel=0,control=64,value=77))
        # Quiet sustained chord, never a rhythmic staccato bass.
        for j,p in enumerate(chords[i]):
            note(st+j*18,st+BAR-48,p,round((38+2*(j==0))*volume))
        pos=0
        for j,(pitch,duration) in enumerate(line):
            assert pitch>=71
            on=st+int(pos*T)
            off=st+int((pos+duration)*T)+(40 if j<len(line)-1 else -20)
            note(on,off,pitch,round((68 if j==0 else 61)*volume))
            pos+=duration
        assert abs(pos-4)<1e-9
        bar+=1
lastbar=bar*BAR
add(lastbar-24,1,mido.Message('control_change',channel=0,control=64,value=0))
add(lastbar+84,1,mido.Message('control_change',channel=0,control=64,value=89))
for j,p in enumerate([48,55,60,64,72,76]):
    note(lastbar+j*20,lastbar+int(3.4*T),p,49 if p>=72 else 39)
add(lastbar+int(3.8*T),1,mido.Message('control_change',channel=0,control=64,value=0))
events.sort(key=lambda x:(x[0],x[1]))
active=set();previous=0
for time,rank,msg in events:
    if msg.type=='note_on' and msg.velocity:
        assert msg.note not in active, ('overlap',msg.note,time)
        active.add(msg.note)
    elif msg.type=='note_off':
        assert msg.note in active, ('orphan',msg.note,time)
        active.remove(msg.note)
    track.append(msg.copy(time=time-previous));previous=time
assert not active
track.append(mido.MetaMessage('end_of_track',time=2*T))
path=OUT/'Upright_KW_Original_Piano.mid'
m.save(path)
print(f'Extended v5 composition: {bar} bars, {m.length:.1f}s, {len(events)} events, no same-pitch collisions')
