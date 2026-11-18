"""Original 64-bar contrasting suite with approved v5 theme and three new themes."""
from pathlib import Path
import mido

T=480; BAR=T*4
OUT=Path('output');OUT.mkdir(exist_ok=True)
A=[[(76,1),(79,1),(81,1),(79,1)],[(74,1),(76,1),(79,2)],[(81,1.5),(79,.5),(76,1),(72,1)],[(74,1),(76,1),(79,2)],[(81,1),(84,1),(81,1),(79,1)],[(79,1),(76,1),(74,1),(72,1)],[(77,1),(76,1),(74,2)],[(71,1),(74,1),(72,2)]]
B=[[(72,2),(77,1.5),(76,.5)],[(74,1),(72,1),(69,2)],[(72,1.5),(76,.5),(79,2)],[(77,3),(76,1)],[(74,2),(72,1),(69,1)],[(72,1),(74,1),(77,2)],[(76,1.5),(74,.5),(72,2)],[(69,3),(72,1)]]
BA=[[(77,1),(79,1),(81,2)],[(79,2),(77,1),(74,1)],[(76,1),(72,1),(69,2)],[(74,1.5),(76,.5),(77,2)],[(81,1),(79,1),(77,2)],[(76,2),(74,2)],[(72,1),(74,1),(76,1),(72,1)],[(69,4)]]
C=[[(79,.5),(81,.5),(83,1),(86,2)],[(83,1),(81,.5),(79,.5),(78,2)],[(76,.5),(78,.5),(79,1),(83,2)],[(81,1.5),(79,.5),(76,2)],[(79,.5),(81,.5),(83,1),(81,1),(79,1)],[(78,1),(76,1),(74,2)],[(76,.5),(78,.5),(79,1),(81,2)],[(79,2),(74,1),(79,1)]]
CA=[[(83,1),(86,1),(83,1),(81,1)],[(79,2),(78,1),(76,1)],[(79,.5),(78,.5),(76,1),(74,2)],[(76,1),(78,1),(79,2)],[(81,1),(83,1),(86,2)],[(83,1.5),(81,.5),(79,2)],[(78,1),(76,1),(74,1),(72,1)],[(74,2),(79,2)]]
D=[[(81,2.5),(79,.5),(76,1)],[(72,2),(74,2)],[(76,2),(72,1),(69,1)],[(71,3),(72,1)],[(76,2),(74,2)],[(72,1),(69,1),(71,2)],[(74,1.5),(72,.5),(69,2)],[(69,3),(72,1)]]
DA=[[(76,2),(81,2)],[(79,1),(76,1),(72,2)],[(74,2.5),(72,.5),(69,1)],[(71,2),(74,2)],[(76,1.5),(79,.5),(76,2)],[(74,2),(72,2)],[(71,1),(69,1),(67,2)],[(69,4)]]
AC=[[48,55,59],[47,55,59],[45,52,60],[43,52,59],[41,48,57],[40,48,55],[50,57,60],[43,50,59]]
BC=[[41,48,57],[45,52,60],[50,57,60],[48,55,60],[41,48,57],[46,53,58],[43,50,58],[48,55,60]]
CC=[[43,50,59],[42,50,57],[40,47,55],[45,52,57],[43,50,59],[47,54,59],[48,55,60],[43,50,59]]
DC=[[45,52,60],[41,48,57],[50,57,60],[40,47,55],[41,48,57],[45,52,60],[43,50,59],[45,52,60]]
sections=[('Original v5 theme',A,AC,76,.88,'chord'),('New lyric theme',B,BC,70,.80,'chord'),('Lyric answer',BA,BC,72,.84,'chord'),('New brighter theme',C,CC,88,.90,'rolling'),('Bright answer',CA,CC,86,.89,'rolling'),('New quiet minor theme',D,DC,67,.73,'sparse'),('Minor answer',DA,DC,69,.76,'sparse'),('Return of v5',A,AC,76,.87,'chord')]
m=mido.MidiFile(ticks_per_beat=T);track=mido.MidiTrack();m.tracks.append(track)
track.append(mido.Message('program_change',channel=0,program=0,time=0))
ev=[]
def event(t,rank,msg):ev.append((int(t),rank,msg))
def note(st,end,p,vel):
    assert end>st
    event(st,2,mido.Message('note_on',channel=0,note=p,velocity=int(vel)))
    event(end,0,mido.Message('note_off',channel=0,note=p,velocity=0))
def cc(t,v):event(max(0,t),1,mido.Message('control_change',channel=0,control=64,value=v))
bar=0
for name,melody,harmony,bpm,volume,style in sections:
    print('SECTION',name,'bar',bar+1)
    for i,line in enumerate(melody):
        st=bar*BAR
        event(st,1,mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(bpm-(2 if i==7 else 0))))
        cc(st if bar==0 else st-30,0)
        cc(st+125,70)
        voices=harmony[i]
        if style=='chord':
            for k,p in enumerate(voices):note(st+12*k,st+BAR-25,p,(40 if k==0 else 34)*volume)
        elif style=='rolling':
            for k,p in enumerate(voices):note(st+50*k,st+BAR-20,p,(38 if k==0 else 33)*volume)
        else:
            for k,p in enumerate(voices[:2]):note(st+20*k,st+BAR-26,p,34*volume)
        beat=0
        for k,(p,d) in enumerate(line):
            note(st+round(beat*T),st+round((beat+d)*T)+(26 if k<len(line)-1 else -15),p,(69 if k==0 else 62)*volume)
            beat+=d
        assert beat==4
        bar+=1
end=bar*BAR
cc(end-20,0);cc(end+80,80)
for k,p in enumerate([48,55,60,64,72,76]):note(end+k*17,end+4*T,p,39+2*k)
cc(end+int(4.5*T),0)
ev.sort(key=lambda e:(e[0],e[1]))
active=set();last=0
for t,_,msg in ev:
    if msg.type=='note_on' and msg.velocity>0:
        assert msg.note not in active,('overlap',msg.note,t)
        active.add(msg.note)
    elif msg.type=='note_off':
        assert msg.note in active,('orphan',msg.note,t)
        active.remove(msg.note)
    track.append(msg.copy(time=t-last));last=t
assert not active
track.append(mido.MetaMessage('end_of_track',time=T*2))
path=OUT/'V7_Contrasting_Original.mid';m.save(path)
print('Generated:',path,'bars:',bar,'duration:',round(m.length,1),'seconds')
