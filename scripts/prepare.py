"""Render a configured episode's narration and derive a frame-accurate timeline."""
import hashlib, json, math, os, pathlib, subprocess, urllib.request
os.environ.setdefault('OMP_NUM_THREADS','2')
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
ROOT=pathlib.Path(__file__).resolve().parents[1]
episode_path=pathlib.Path(os.environ.get('EPISODE',str(ROOT/'episodes/001-visa-mastercard.json'))).resolve()
e=json.loads(episode_path.read_text()); cache=ROOT/'.cache/tts';cache.mkdir(parents=True,exist_ok=True)
assets={'kokoro-v1.0.onnx':'model-files-v1.0/kokoro-v1.0.onnx','voices-v1.0.bin':'model-files-v1.0/voices-v1.0.bin'}
for name,remote in assets.items():
 p=cache/name
 if not p.exists():
  tmp=p.with_suffix('.part');urllib.request.urlretrieve('https://github.com/thewh1teagle/kokoro-onnx/releases/download/'+remote,tmp);tmp.replace(p)
# These expected SHA256 values are recorded after the original verified-TLS download.
manifest=ROOT/'docs/tts-checksums.json'
if manifest.exists():
 for name,digest in json.loads(manifest.read_text()).items():
  if hashlib.sha256((cache/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('TTS checksum mismatch: '+name)
engine=Kokoro(str(cache/'kokoro-v1.0.onnx'),str(cache/'voices-v1.0.bin'))
out=ROOT/'public/audio';chunks=out/'chunks';chunks.mkdir(parents=True,exist_ok=True)
rate=24000;fps=e['fps'];cursor=0;audio=[];timeline=[];caps=[]
for i,s in enumerate(e['scenes']):
 key=hashlib.sha256(json.dumps([s['text'],e['voice'],e['speed']]).encode()).hexdigest()[:16]
 p=chunks/(key+'.wav')
 if p.exists():samples,sr=sf.read(p)
 else:
  samples,sr=engine.create(s['text'],voice=e['voice'],speed=e['speed'],lang='en-us');sf.write(p,samples,sr)
 assert sr==rate
 # Pause breath at the end of each scene, and quantize to whole frames.
 lead=0.10;frames=max(102,math.ceil((len(samples)/sr+lead+0.23)*fps))
 scene_audio=np.concatenate([np.zeros(round(lead*sr)),samples])
 scene_audio=np.pad(scene_audio,(0,round(frames*sr/fps)-len(scene_audio)))
 timeline.append({**s,'from':cursor,'duration':frames,'audioStart':cursor/fps+lead,'audioEnd':cursor/fps+lead+len(samples)/sr})
 caps.append({'start':cursor/fps+lead,'end':cursor/fps+lead+len(samples)/sr,'text':s['text']})
 audio.append(scene_audio);cursor+=frames;print(i+1,frames,round(len(samples)/sr,2),s['text'],flush=True)
# Small tail so the final thought is not clipped.
audio.append(np.zeros(rate//2));cursor+=fps//2
raw=out/'narration-raw.wav';sf.write(raw,np.concatenate(audio),rate)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af','loudnorm=I=-16:TP=-1.5:LRA=7','-ar',str(rate),str(out/'narration.wav')],check=True);raw.unlink()
result={**e,'durationInFrames':cursor,'scenes':timeline,'captions':caps,'audio':'audio/narration.wav'}
(ROOT/'episodes/generated.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'episodes/script.md').write_text('# Final narration\n\n'+'\n\n'.join(s['text'] for s in e['scenes'])+'\n')
(ROOT/'episodes/storyboard.md').write_text('# Storyboard\n\n| Seconds | Scene | Visual | Narration | Claim |\n|---|---|---|---|---|\n'+'\n'.join(f"| {s['from']/fps:.2f}–{(s['from']+s['duration'])/fps:.2f} | {s['eyebrow']} | {s['kind']} — {' / '.join(s['title'])} | {s['text']} | {s['claim']} |" for s in timeline)+'\n')
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(ROOT/'output/captions.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(caps))+'\n')
(ROOT/'episodes/publishing.json').write_text(json.dumps(e['publishing'],indent=2)+'\n')
print('Total duration:',cursor/fps,'seconds; words:',sum(len(s['text'].split()) for s in e['scenes']))
if not 45<=cursor/fps<=60:raise RuntimeError('Adjust pacing: duration outside Short requirements')
