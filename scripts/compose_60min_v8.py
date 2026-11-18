"""60-minute six-chapter original KAWAI piano arrangement.

Reuses the APPROVED original v7 melodic phrases. Each chapter explores a
distinct family of themes, dynamics, register, tempo and left hand texture.
The same short MP3 is never copied to fill the whole hour.
"""
from pathlib import Path
import importlib.util
import mido

# Bring in the composed v7 melodies and voicings as the common source.
spec=importlib.util.spec_from_file_location("v7", "scripts/compose_contrasting_v7.py")
v7=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v7)

T=480
BAR=T*4
OUT=Path("output");OUT.mkdir(exist_ok=True)
# Chapter name, BPM, verse patterns, harmonic palette, accompaniment, dynamics.
chapters=[
 ("01 Warm opening",76,[(v7.A,v7.AC),(v7.B,v7.BC)],"chord",.82),
 ("02 Lyrical and spacious",70,[(v7.B,v7.BC),(v7.BA,v7.BC)],"soft",.78),
 ("03 Bright moving piano",88,[(v7.C,v7.CC),(v7.CA,v7.CC)],"rolling",.88),
 ("04 Reflective and quiet",68,[(v7.D,v7.DC),(v7.DA,v7.DC)],"sparse",.74),
 ("05 Gentle forward motion",82,[(v7.CA,v7.CC),(v7.BA,v7.BC),(v7.C,v7.CC)],"flow",.84),
 ("06 Return and resolution",74,[(v7.A,v7.AC),(v7.B,v7.BC),(v7.D,v7.DC)],"chord",.76),
]

def compose_chapter(index,config):
    title,bpm,phrases,style,loud=config
    midi=mido.MidiFile(ticks_per_beat=T)
    track=mido.MidiTrack();midi.tracks.append(track)
    track.append(mido.Message("program_change",channel=0,program=0,time=0))
    events=[]
    def e(t,priority,msg):
        events.append((max(0,int(round(t))),priority,msg))
    def note(st,ed,p,vel):
        assert ed>st and 21<=p<=108
        e(st,2,mido.Message("note_on",note=p,velocity=max(1,min(115,round(vel))),channel=0))
        e(ed,0,mido.Message("note_off",note=p,velocity=0,channel=0))
    def pedal(t,value):
        e(t,1,mido.Message("control_change",control=64,value=value,channel=0))
    bars=0
    # Compose enough score to cover the complete 10 minutes plus tail;
    # not a short fixed audio loop.
    elapsed=0
    while elapsed<608:
        phrase_idx=(bars//8)%len(phrases)
        phrase,chords=phrases[phrase_idx]
        line_idx=bars%8
        line=phrase[line_idx]
        harmony=chords[line_idx]
        start=bars*BAR
        # Accent phrasing and mild tempo shape at each musical cadence.
        speed=bpm-(2 if line_idx==7 else 0)+(1 if bars%32 in range(8,16) else 0)
        e(start,1,mido.MetaMessage("set_tempo",tempo=mido.bpm2tempo(speed)))
        pedal(start-20 if bars else 0,0)
        pedal(start+90,76 if style not in ("sparse","soft") else 66)
        weight=loud*(.94+.07*(1-abs((bars%8)-3.5)/3.5))
        if style=="chord":
            fig=[(0,harmony[0],3.85),(0.04,harmony[1],3.78),(0.09,harmony[2],3.72)]
        elif style=="soft":
            fig=[(0,harmony[0],3.82),(.08,harmony[1],3.7)]
        elif style=="sparse":
            fig=[(0,harmony[0],3.78),(.20,harmony[1],3.50)]
        elif style=="rolling":
            fig=[(0,harmony[0],3.85),(.26,harmony[1],3.58),(.48,harmony[2],3.37)]
        else:
            fig=[(0,harmony[0],3.82),(.12,harmony[1],3.65),(.35,harmony[2],3.45)]
        for j,(b,p,d) in enumerate(fig):
            note(start+b*T,start+(b+d)*T,p,(38 if j==0 else 33)*weight)
        pos=0
        for j,(p,d) in enumerate(line):
            # Original melody is intact. Tiny expressive dynamic shapes only.
            register=p
            if index==4 and bars%32 in range(24,32):
                # Gentle lower-register answer late in reflective chapter.
                register=max(60,p-12)
            vel=(69 if j==0 else 62)*weight
            note(start+pos*T,start+(pos+d)*T+(25 if j<len(line)-1 else -10),register,vel)
            pos+=d
        assert abs(pos-4)<1e-8
        bars+=1
        elapsed+=240/speed
    # No simultaneous same-key note attacks in this orchestration.
    events.sort(key=lambda x:(x[0],x[1]))
    active=set();last=0
    for t,_,msg in events:
        if msg.type=="note_on" and msg.velocity>0:
            assert msg.note not in active,("collision",title,msg.note,t)
            active.add(msg.note)
        elif msg.type=="note_off":
            assert msg.note in active,("orphan",title,msg.note,t)
            active.remove(msg.note)
        track.append(msg.copy(time=t-last));last=t
    assert not active
    track.append(mido.MetaMessage("end_of_track",time=2*T))
    filename=OUT/f"chapter_{index:02d}.mid"
    midi.save(filename)
    print(f"{title}: {bars} bars, {midi.length:.1f} sec, {filename}")
    assert midi.length>=600
    return filename

for i,conf in enumerate(chapters,1):
    compose_chapter(i,conf)
