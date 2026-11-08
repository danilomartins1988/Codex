"""Validate the real MP4; preserve failed outcomes rather than masking them."""
import json, pathlib, subprocess, hashlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1];e=json.loads((ROOT/'episodes/generated.json').read_text());p=ROOT/'output'/e['filename']
def run(args):return subprocess.run(args,capture_output=True,text=True,check=True)
probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]).stdout)
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
checks={
 'video_h264':v['codec_name']=='h264','audio_aac':a['codec_name']=='aac',
 'resolution':(v['width'],v['height'])==(1080,1920), 'fps_30':v['avg_frame_rate']=='30/1',
 'duration_45_to_60':45<=float(probe['format']['duration'])<=60,
 'frame_count':int(v['nb_read_frames'])==e['durationInFrames'],
 'audio_video_duration_difference_lt_0_1s':abs(float(v['duration'])-float(a['duration']))<.1,
 'timeline_contiguous':all(e['scenes'][i]['from']+e['scenes'][i]['duration']==e['scenes'][i+1]['from'] for i in range(len(e['scenes'])-1)),
 'captions_match_script':all(c['text']==s['text'] for c,s in zip(e['captions'],e['scenes'])) and len(e['captions'])==len(e['scenes']),
 'caption_intervals_valid':all(s['from']/e['fps']<=c['start']<c['end']<=(s['from']+s['duration'])/e['fps'] for c,s in zip(e['captions'],e['scenes'])),
 'all_12_scenes_present':len(e['scenes'])==12,
 'one_mp4_only':len(list((ROOT/'output').glob('*.mp4')))==1
}
decode=run(['ffmpeg','-v','info','-i',str(p),'-vf','blackdetect=d=0.08:pix_th=0.015:pic_th=0.98','-af','silencedetect=n=-45dB:d=1.2,volumedetect','-f','null','-'])
(ROOT/'output/decode-analysis.log').write_text(decode.stderr)
checks['full_decode_no_errors']=not bool(re.search(r'Error while|Invalid data|corrupt',decode.stderr,re.I))
checks['no_full_black_frames']='black_start:' not in decode.stderr
checks['no_unexpected_long_silence']='silence_start:' not in decode.stderr
m=re.search(r'max_volume: ([\-\d.]+) dB',decode.stderr);checks['audio_present_and_not_clipped']=bool(m and -12<float(m[1])<0)
research=json.loads((ROOT/'research/claims.json').read_text())
report={'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'durationSeconds':float(probe['format']['duration']),'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'frames':int(v['nb_read_frames']),'videoCodec':v['codec_name'],'audioCodec':a['codec_name'],'checks':checks,'technicalPassed':all(checks.values()),'editorialStatus':research['status'],'captionGranularity':'Sentence-level, tied to individually synthesized speech segments; no word-level forced alignment.','manualReview':{'contactSheet':'12 representative Remotion scene frames inspected; post-encode frames still require comparison.','audio':'Neural en-US af_heart voice generated. Signal tested; naturalness and pronunciation require human listening review.','mobile':'46px sentence captions, 84px headlines. Safe region left 90/right 180, top 140/bottom 350 for essential captions; YouTube UI varies.'},'externalDelivery':'Pending remote Git push and retrieval verification; see DELIVERY.md.'}
(ROOT/'output/ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n');(ROOT/'output/qa.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'docs/QA.md').write_text('# Quality assurance\n\n'+f"Technical checks: {'PASS' if report['technicalPassed'] else 'FAIL'}. Duration: {report['durationSeconds']:.3f}s. H.264 / AAC, 1080×1920, 30 fps.\n\n"+'\n'.join(f"- {'PASS' if value else 'FAIL'}: {name}" for name,value in checks.items())+'\n\nEditorial: '+research['status']+'. Primary sources were blocked; publication clearance is pending.\n\nCaptions are sentence-level, matched to separately synthesized sentence audio, not word-level aligned. Audio signal is checked; perceptual voice quality still needs human listening. No background music or third-party sound effects are used.\n')
print(json.dumps(report,indent=2))
if not report['technicalPassed']:raise SystemExit(1)
