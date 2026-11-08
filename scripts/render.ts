import {bundle} from '@remotion/bundler';
import {renderMedia,selectComposition,renderStill} from '@remotion/renderer';
import path from 'node:path';
import {mkdirSync} from 'node:fs';
import episode from '../episodes/generated.json';
const root=process.cwd();
const browserExecutable=process.env.CHROME_PATH??'/usr/bin/chromium';
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.ts')});
const composition=await selectComposition({serveUrl,id:'HiddenEconomics',browserExecutable});
mkdirSync('output/frames',{recursive:true});
if(process.argv.includes('--stills')){
 for(const [i,s] of episode.scenes.entries())await renderStill({serveUrl,composition,frame:s.from+Math.floor(s.duration*.6),output:`output/frames/${String(i+1).padStart(2,'0')}.png`,browserExecutable});
}else{
 let last=-1;
 await renderMedia({serveUrl,composition,codec:'h264',audioCodec:'aac',pixelFormat:'yuv420p',crf:19,outputLocation:path.join(root,'output',episode.filename),browserExecutable,concurrency:3,x264Preset:'fast',onProgress:({progress})=>{const p=Math.floor(progress*100/10)*10;if(p!==last){console.log(`Render ${p}%`);last=p;}}});
}
