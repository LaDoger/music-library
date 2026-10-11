#!/usr/bin/env node
/* Targeted annotated-score UI/drift checks. One Chromium instance; no audio files.
   ANALYSIS_BASE=http://127.0.0.1:8765/ ANALYSIS_SHOTS=/tmp/music-analysis-shots
   NODE_PATH=/tmp/music-ui-review/node_modules node scripts/analysis/check_analysis.cjs */
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const {chromium}=require('playwright');
const {measureDrift,truthFor}=require('../watch_drift.cjs');
const ALL_IDS=['lyadov_op11no1_prelude_op_11_no_1_anatoly_l','schumann_op15_schumann_kinderszenen_op_15__no10','kalinnikov_vasili_kalinnikov_sinfonia_nb2'];
const IDS=process.env.ANALYSIS_ONLY ? ALL_IDS.filter(id=>id===process.env.ANALYSIS_ONLY) : ALL_IDS;
const BASE=process.env.ANALYSIS_BASE||'http://127.0.0.1:8765/';
const SHOTS=process.env.ANALYSIS_SHOTS||'/tmp/music-analysis-shots';fs.mkdirSync(SHOTS,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_BIN||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});
 const errors=[];let page;
 const fresh=async(viewport={width:1440,height:900})=>{if(page)await page.close();page=await browser.newPage({viewport});page.on('pageerror',e=>errors.push(e.message));};
 await fresh();
 const partial=path.join(SHOTS,'results.partial.json');
 const results=process.env.ANALYSIS_SKIP_MATRIX&&fs.existsSync(partial)?JSON.parse(fs.readFileSync(partial)).results:[];
 const progress=drifts=>fs.writeFileSync(partial,JSON.stringify({base:BASE,results,drifts,errors},null,2)+'\n');
 try{
  if(!process.env.ANALYSIS_SKIP_MATRIX) for(const [width,height] of [[1440,900],[390,844]]){
   await page.setViewportSize({width,height});
   for(const id of IDS){
    await page.goto(BASE+'?watch='+id+'&analysis=1&sound=salamander');
    await page.waitForFunction(i=>window.__watch?.id===i&&window.__watch.ready,id,{timeout:150000});
    let state=await page.evaluate(()=>{const {play,seek,...s}=window.__watch;return s});
    assert(state.hasScore&&state.hasAnalysis&&state.analysisOn&&state.audioSrc==='score',JSON.stringify(state));
    const svgTexts=()=>page.locator('#wOsmd svg text').allTextContents();
    const onTexts=await svgTexts();
    assert(onTexts.some(t=>/Bm|G#m|F#m/.test(t)),'harmony visible');
    const layout=async()=>{
     const r=await page.evaluate(()=>{
      const box=s=>document.querySelector(s).getBoundingClientRect();
      const d=document.scrollingElement;
      const slide=box('#wSlide');const text=[...document.querySelectorAll('#wOsmd svg text')].map(e=>e.getBoundingClientRect()).filter(b=>b.width);
      return {width:d.scrollWidth,vw:innerWidth,height:d.scrollHeight,vh:innerHeight,stage:box('#wStage').top,
       header:box('#wAnalysisHeader').bottom,title:box('#wTitle').bottom,
       textMin:Math.min(...text.map(b=>b.left)),textMax:Math.max(...text.map(b=>b.right)),slideLeft:slide.left,slideRight:slide.right};
     });
     assert(r.width<=r.vw+1,'horizontal overflow '+JSON.stringify(r));
     assert(r.height>r.vh+1,'page must scroll '+JSON.stringify(r));
     assert(r.title<=r.stage+1&&r.header<=r.stage+1,'header above score '+JSON.stringify(r));
     assert(r.textMin>=r.slideLeft-2&&r.textMax<=r.slideRight+2,'score text clipped at horizontal edge '+JSON.stringify(r));
     return r;
    };
    const first=await layout();
    for(const frac of [0,.42,.86]){
     await page.evaluate(f=>window.__watch.seek(window.__watch.total*f),frac);await sleep(900);
     assert(await page.locator('#wHarmony').textContent(),'bar/chord header');
     await page.screenshot({path:path.join(SHOTS,`${id}_${width}_on_${Math.round(frac*100)}.png`)});
    }
    await page.click('#wAnalysis');
    await page.waitForFunction(()=>!document.querySelector('#wAnalysis').disabled&&!window.__watch.analysisOn);
    assert.equal(new URL(page.url()).searchParams.get('analysis'),'0');
    assert.equal(await page.evaluate(()=>localStorage.getItem('watchAnalysis')),'0');
    assert(!(await svgTexts()).some(t=>/Bm|G#m|F#m/.test(t)),'harmony hidden');
    const off=await layout();
    await page.screenshot({path:path.join(SHOTS,`${id}_${width}_off_86.png`)});
    await page.keyboard.press('a');
    await page.waitForFunction(()=>!document.querySelector('#wAnalysis').disabled&&window.__watch.analysisOn);
    assert.equal(new URL(page.url()).searchParams.get('analysis'),'1');
    // On/off is an engraving-only change; source timeline stays the same.
    assert.equal(await page.evaluate(()=>window.__watch.total),state.total);
    await page.click('#wPlay');await page.waitForFunction(()=>window.__watch.playing);
    const start=await page.evaluate(()=>window.__watch.baseTime);await sleep(1400);
    assert((await page.evaluate(()=>window.__watch.baseTime))>start+.5,'playback advances');
    await page.click('#wAnalysis');
    await page.waitForFunction(()=>!document.querySelector('#wAnalysis').disabled&&!window.__watch.analysisOn);
    assert(await page.evaluate(()=>window.__watch.playing),'toggle preserves live audio');
    await page.click('#wPlay');
    // URL wins over storage, storage wins over the default, explicit default on.
    await page.goto(BASE+'?watch='+id+'&sound=salamander');
    await page.waitForFunction(()=>window.__watch?.ready,{},{timeout:150000});
    assert(!(await page.evaluate(()=>window.__watch.analysisOn)),'persisted off state');
    results.push({id,width,height,layout:first,offLayout:off});
    progress([]);console.log('PASS layout/toggle/playback',id,width+'x'+height);
    await fresh({width,height});
   }
  }
  // Debug/fallback MIDI must respect a sub-piece range rather than play the set.
  await page.goto(BASE+'?watch='+ALL_IDS[1]+'&analysis=1&audio=midi&sound=salamander');
  await page.waitForFunction(()=>window.__watch?.ready,{},{timeout:150000});
  assert((await page.evaluate(()=>window.__watch.total))<150,'MIDI fallback sliced to No. 10');
  assert((await page.evaluate(()=>window.__watch.audioSrc)).startsWith('midi'),'forced MIDI fallback');
  await page.evaluate(()=>localStorage.removeItem('watchAnalysis'));
  await page.goto(BASE+'?watch='+IDS[0]+'&sound=salamander');
  await page.waitForFunction(()=>window.__watch?.ready,{},{timeout:150000});
  assert(await page.evaluate(()=>window.__watch.analysisOn),'default on when bundle exists');
  await page.setViewportSize({width:1440,height:900});
  const truths=truthFor(IDS);const drifts=[];await fresh();
  for(const id of IDS){
   const d=await measureDrift(page,BASE,id,truths[id],{extra:'&analysis=1'});
   assert(d.n>=6&&d.max<1,'independent drift <1 beat: '+id+' '+JSON.stringify(d));drifts.push(d);progress(drifts);console.log('PASS drift',id,d.max,d.n);await fresh();
  }
  assert.deepEqual(errors,[],'page errors');
  fs.writeFileSync(path.join(SHOTS,'results.json'),JSON.stringify({base:BASE,results,drifts,errors},null,2)+'\n');
  console.log('PASS all annotated-score checks; results '+path.join(SHOTS,'results.json'));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
