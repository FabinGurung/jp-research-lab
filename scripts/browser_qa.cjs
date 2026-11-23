#!/usr/bin/env node
"use strict";
/* Real Chromium QA of generated, PUBLIC static portal. No Google Drive, APIs or mutation. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { chromium } = require("playwright");
const { AxeBuilder } = require("@axe-core/playwright");
const root = path.resolve(__dirname, "..");
const base = "http://127.0.0.1:8765/";
const out = path.join(root, "browser-qa-output");
fs.mkdirSync(out, {recursive:true});
const findings = [];
const failures = [];
function record(name, detail) { findings.push({name, ...detail});console.log("BROWSER_QA",name,JSON.stringify(detail)); }
async function check(name, task) {
 try { await task(); record(name, {status:"PASS"}); }
 catch(err) { failures.push({name, error:String(err&&err.stack||err)});record(name,{status:"FAIL",error:String(err&&err.message||err)}); }
}
function assertNoOverflow(page, description) {
 return page.evaluate(({description}) => {
  const full=document.documentElement.scrollWidth, viewport=window.innerWidth;
  if(full>viewport+2) throw Error(description+" horizontal overflow "+full+" > "+viewport);
 }, {description});
}
async function main() {
 const server=spawn("python3",["-m","http.server","8765","--bind","127.0.0.1","--directory","dist"],{cwd:root,stdio:"ignore"});
 let browser;
 try {
  for(let i=0;i<55;i++){
   try{ const response=await fetch(base); if(response.ok)break; }catch(_){}
   await new Promise(r=>setTimeout(r,100));
  }
  browser=await chromium.launch({headless:true});
  const desktop=await browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1,permissions:["clipboard-read","clipboard-write"]});
  const page=await desktop.newPage();
  const javascriptErrors=[];
  page.on("pageerror",e=>javascriptErrors.push(String(e)));
  await check("desktop_hero_and_screenshot",async()=>{
   await page.goto(base,{waitUntil:"networkidle"});
   await page.locator("[data-winged-book]").waitFor();
   assert.equal(await page.locator("[data-motion-toggle]").count(),1);
   assert.ok((await page.locator("h1").first().innerText()).includes("One workspace."));
   assert.equal(await page.locator("#site-nav-links a").count(),3);
   assert.equal(await page.locator('a[href="academic-writing/index.html"]').count()>=1,true);
   assert.equal(await page.locator('a[href="enterprise-documents/index.html"]').count()>=1,true);
   await assertNoOverflow(page,"desktop");
   await page.screenshot({path:path.join(out,"desktop-home.png"),fullPage:true,animations:"disabled"});
  });
  await check("two_family_research_and_template_audit",async()=>{
   await page.goto(base+"academic-writing/",{waitUntil:"networkidle"});
   assert.ok((await page.locator("h1").innerText()).includes("Research, theses"));
   assert.ok(await page.getByText("Thesis infrastructure",{exact:true}).count()>=1);
   assert.ok(await page.locator('a[href="../researchers/index.html"]').count()>=1);
   await assertNoOverflow(page,"academic writing");
   await page.goto(base+"academic-writing/control-tower/",{waitUntil:"networkidle"});
   assert.ok((await page.locator("h1").innerText()).includes("Academic Writing Control"));
   await page.goto(base+"enterprise-documents/template-audit/",{waitUntil:"networkidle"});
   assert.ok((await page.locator("h1").innerText()).includes("Template normalization"));
   assert.equal(await page.locator("tbody").first().locator("tr").count(),14);
   assert.equal(await page.locator("tbody").last().locator("tr").count(),5);
   await assertNoOverflow(page,"enterprise template audit");
   await page.goto(base,{waitUntil:"networkidle"});
  });
  await check("fabin_researcher_curved_gallery_without_level_one_frame",async()=>{
   await page.goto(base+"researchers/fabin-gurung/index.html",{waitUntil:"networkidle"});
   await page.locator('.lanes.arc-stage').first().waitFor();
   assert.equal(await page.getByRole('link',{name:/Open interactive frame viewer/}).count(),0);
    assert.ok((await page.locator('a[href="experiments/four-workflows/index.html"]').count())>=1);
   assert.ok((await page.locator('.record-details').count())>=1);
   assert.equal(await page.locator('a[href="../../assets/arc-gallery.css"]').count(),0);
   const first=page.locator('.arc-toolbar').first();
   const initial=await first.locator('.arc-count').innerText();
   await first.locator('button[aria-label="Next card"]').click();
   assert.notEqual(await first.locator('.arc-count').innerText(),initial);
   await first.getByRole('button',{name:'View all cards'}).click();
   assert.ok(await page.locator('.arc-stage.arc-expanded').count()>=1);
   await assertNoOverflow(page,'Fabin researcher carousel');
   await page.screenshot({path:path.join(out,'fabin-researcher-curved-gallery.png'),fullPage:true,animations:'disabled'});
  });
  await check("fabin_four_workflows_desktop",async()=>{
   await page.goto(base+"researchers/fabin-gurung/experiments/four-workflows/",{waitUntil:"networkidle"});
   await page.locator('#building [data-element="S1"]').waitFor();
   assert.equal(await page.locator('#source-state').innerText().then(x=>x.includes('snapshot read')),true);
   assert.equal(await page.locator('#building [data-element]').evaluateAll(els=>new Set(els.map(e=>e.dataset.element)).size),9);
   await page.locator('[data-view="plan"]').click();
   await page.locator('#building [data-element="C2"]').click();
   assert.ok((await page.locator('#selection h3').innerText()).includes('Column C2'));
   await page.locator('[data-tab="estimate"]').click();
   assert.ok((await page.locator('#cost-table').innerText()).includes('55,080'));
   await page.locator('[data-tab="schedule"]').click();
   assert.equal(await page.locator('#schedule-table tr').count(),9);
   await page.locator('[data-tab="drawings"]').click();
   await assertNoOverflow(page,'Fabin desktop experiment');
   await page.screenshot({path:path.join(out,'fabin-four-workflows-desktop.png'),fullPage:true,animations:'disabled'});
   await page.goto(base,{waitUntil:'networkidle'});
  });
  await check("fabin_spatial_frame_views",async()=>{
   const route=base+"researchers/fabin-gurung/experiments/four-workflows/frame.html";
   const frameDesktop=await browser.newContext({viewport:{width:980,height:850},deviceScaleFactor:2});
   const frameMobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
   const fp=await frameDesktop.newPage(), fm=await frameMobile.newPage();
   fp.on("pageerror",e=>javascriptErrors.push(String(e)));
   fm.on("pageerror",e=>javascriptErrors.push(String(e)));
   const expected={moment:"14.868",shear:"16.969",axial:"40.6875",torsion:"Outside the model",
    movement:"−0.450",rebar:"335.83",reactions:"162.75"};
   fs.mkdirSync(path.join(out,"fabin-frame"),{recursive:true});
   try{
    for(const [view,value] of Object.entries(expected)){
     await fp.goto(route+"?view="+view);
     await fp.locator('#frame-panel[data-active="'+view+'"]').waitFor();
     assert.equal(await fp.locator('[role=tab][aria-selected=true]').count(),1);
     const labels=await fp.locator('#frame-drawing text').allTextContents();
     assert.ok(["C1","C2","C3","C4","B1","B2","B3","B4","S1"].every(id=>labels.includes(id)));
     assert.equal(await fp.locator("#frame-values th").count(),3);
     assert.equal(await fp.locator("#frame-highlights .frame-stat").count(),4);
     assert.ok((await fp.locator("#frame-values").innerText()).includes(value));
     await assertNoOverflow(fp,"Desktop frame "+view);
     await fp.evaluate(()=>document.fonts.ready);
     await fp.locator("#frame-evidence").screenshot({path:path.join(out,"fabin-frame",view+".png"),animations:"disabled"});
     await fm.goto(route+"?view="+view);
     await fm.locator('#frame-panel[data-active="'+view+'"]').waitFor();
     await assertNoOverflow(fm,"Mobile frame "+view);
    }
    await fp.locator("#view-reactions").focus();
    await fp.keyboard.press("ArrowRight");
    assert.equal(await fp.locator("#frame-panel").getAttribute("data-active"),"moment");
    await fp.getByRole("tab",{name:"Reinforcement"}).click();
    assert.match(fp.url(),/view=rebar$/);
   }finally{
    await frameDesktop.close();
    await frameMobile.close();
   }
  });
  await check("fabin_threejs_member_details_and_column_curve",async()=>{
    try {
    const route=base+"researchers/fabin-gurung/experiments/four-workflows/";
    await page.goto(route+"frame.html?view=movement",{waitUntil:"networkidle"});
    assert.ok((await page.locator("#frame-values").innerText()).includes("−0.13039"));
    assert.ok((await page.locator("#frame-drawing").textContent()).includes("Column"));
    assert.ok(await page.locator('a[href="detail.html"]').count()>=1);
    const model=await page.evaluate(()=>fetch('frame-results.json').then(r=>r.json()));
    assert.ok(model.column_flexure);
    assert.ok(Math.abs(model.column_flexure.peak_z_m-2.0)<1e-8);
    assert.ok(Math.abs(model.column_flexure.peak_chord_relative_mm+0.1303853917)<1e-8);
    await page.goto(route+"detail.html",{waitUntil:"networkidle"});
    await page.locator("#three-stage canvas").waitFor({timeout:30000});
    assert.ok((await page.locator("#render-state").innerText()).includes("Three.js active"));
    assert.ok((await page.locator("#member-metrics").innerText()).includes("−0.45047"));
    fs.mkdirSync(path.join(out,"fabin-member"),{recursive:true});
    for(const name of ["beam","column","slab"]){
      await page.locator('[data-member="'+name+'"]').click();
      assert.equal(await page.locator('[data-member="'+name+'"]').getAttribute("aria-pressed"),"true");
      for(const view of ["3d","elevation","plan","section"]){
        await page.locator('[data-view="'+view+'"]').click();
        assert.equal(await page.locator('[data-view="'+view+'"]').getAttribute("aria-pressed"),"true");
        await page.locator("#three-stage").screenshot({path:path.join(out,"fabin-member",name+"-"+view+".png"),animations:"disabled"});
      }
    }
    await page.locator('[data-member="column"]').click();
    assert.ok((await page.locator("#member-metrics").innerText()).includes("−0.13039"));
    await page.locator('[data-layout="concept"]').click();
    assert.ok((await page.locator("#member-steel").innerText()).includes("geometric concept only"));
    await assertNoOverflow(page,"Fabin Three.js desktop details");
    await page.screenshot({path:path.join(out,"fabin-threejs-member-details.png"),fullPage:true,animations:"disabled"});
    } finally { await page.goto(base,{waitUntil:"networkidle"}); }
  });
  await check("desktop_pause_and_resume",async()=>{
   const btn=page.locator("[data-motion-toggle]");
   await btn.click();
   assert.equal(await btn.getAttribute("aria-pressed"),"true");
   assert.equal(await page.locator(".flying-book").evaluate(e=>getComputedStyle(e).animationPlayState),"paused");
   await btn.click();
   assert.equal(await btn.getAttribute("aria-pressed"),"false");
  });
  await check("day_night_switch",async()=>{
   const btn=page.locator("[data-theme-toggle]");
   await btn.click();
   assert.equal(await page.locator("html").getAttribute("data-theme"),"dusk");
   await page.screenshot({path:path.join(out,"desktop-dusk.png"),animations:"disabled"});
  });
  await check("keyboard_navigation",async()=>{
   await page.keyboard.press("Tab");
   const active=await page.evaluate(()=>({
    tag:document.activeElement?.tagName,
    visible:document.activeElement?getComputedStyle(document.activeElement).visibility:""
   }));
   assert.ok(["A","BUTTON","INPUT","SELECT","TEXTAREA"].includes(active.tag),JSON.stringify(active));
   assert.notEqual(active.visible,"hidden");
  });
  await check("owner_prompt_copy",async()=>{
   await page.goto(base+"owner-prompts/fabin-gurung/",{waitUntil:"networkidle"});
   const text=await page.locator("#owner-prompt-text").inputValue();
   assert.ok(text.length>4000);
   assert.ok(text.includes("RSH-001"));
   await page.locator("[data-copy-owner-prompt]").click();
   await page.waitForFunction(() => document.querySelector("[data-copy-status]")?.textContent?.startsWith("Copied."),null,{timeout:7000});
   assert.equal(await page.locator("[data-copy-status]").innerText(),"Copied. Paste it only in this researcher's own chat.");
   const clip=await page.evaluate(()=>navigator.clipboard.readText());
   assert.equal(clip,text);
   await page.screenshot({path:path.join(out,"desktop-owner-prompt.png"),fullPage:true,animations:"disabled"});
  });
  await check("researcher_routes_and_portal_navigation",async()=>{
   for(const route of ["start-here/","search/","researchers/","thesis-infrastructure/","owner-prompts/","branches/","controls/latex/","roadmap/","how-to/"]){
    const response=await page.goto(base+route,{waitUntil:"domcontentloaded"});
    assert.equal(response.status(),200,route);
    assert.ok(await page.locator("main").count(),route);
   }
  });
  await check("catalogue_search_and_filter",async()=>{
   await page.goto(base+"search/",{waitUntil:"networkidle"});
   await page.locator(".search-result").first().waitFor();
   await page.locator("#research-search").fill("Safal");
   await page.waitForFunction(() => Number(document.querySelectorAll(".search-result").length)>0);
   assert.ok((await page.locator("#search-summary").innerText()).includes("matching catalogue"));
   await page.locator("#research-category").selectOption("Researchers");
   await page.waitForFunction(() => {
     const all=[...document.querySelectorAll(".search-category")];
     return all.length>0 && all.every(x=>x.textContent==="Researchers");
   },null,{timeout:6000});
   const visible=await page.locator(".search-category").allInnerTexts();
   assert.ok(visible.length>0);
   assert.ok(visible.every(x=>x.toLowerCase()==="researchers"));
   await page.screenshot({path:path.join(out,"desktop-search.png"),fullPage:true,animations:"disabled"});
   await page.locator("#research-search").focus();
   await page.keyboard.press("Escape");
   assert.equal(await page.locator("#research-search").inputValue(),"");
  });
  await check("desktop_wcag_axe",async()=>{
   await page.goto(base,{waitUntil:"networkidle"});
   const results=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
   const serious=results.violations.filter(v=>v.impact==="critical"||v.impact==="serious");
   fs.writeFileSync(path.join(out,"axe-desktop.json"),JSON.stringify(results.violations,null,2));
   if(serious.length)throw Error("WCAG serious/critical: "+serious.map(x=>x.id+"("+x.nodes.length+")").join(", "));
  });
  await check("search_page_wcag_axe",async()=>{
   await page.goto(base+"search/",{waitUntil:"networkidle"});
   const results=await new AxeBuilder({page}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
   const serious=results.violations.filter(v=>v.impact==="critical"||v.impact==="serious");
   fs.writeFileSync(path.join(out,"axe-search.json"),JSON.stringify(results.violations,null,2));
   if(serious.length)throw Error("Serious search accessibility findings: "+serious.map(x=>x.id).join(","));
  });
  await desktop.close();

  const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1});
  const mp=await mobile.newPage();
  mp.on("pageerror",e=>javascriptErrors.push(String(e)));
  await check("mobile_390px_navigation_and_screenshot",async()=>{
   await mp.goto(base,{waitUntil:"networkidle"});
   assert.equal(await mp.locator("#site-nav-links a").count(),3);
   await assertNoOverflow(mp,"mobile homepage");
   await mp.screenshot({path:path.join(out,"mobile-home.png"),fullPage:true,animations:"disabled"});
  });
  await check("mobile_menu_keyboard_accessibility",async()=>{
   await mp.goto(base,{waitUntil:"networkidle"});
   const toggle=mp.locator("[data-mobile-menu]");
   const nav=mp.locator("#site-nav-links");
   assert.ok(await toggle.isVisible());
   assert.equal(await nav.isHidden(),true);
   await toggle.click();
   assert.equal(await toggle.getAttribute("aria-expanded"),"true");
   assert.ok(await nav.isVisible());
   await mp.keyboard.press("Escape");
   assert.equal(await toggle.getAttribute("aria-expanded"),"false");
   assert.equal(await nav.isHidden(),true);
   assert.equal(await toggle.evaluate(el=>document.activeElement===el),true);
  });
  await check("mobile_owner_prompt_and_copy_control",async()=>{
   await mp.goto(base+"owner-prompts/safal-dawadi/",{waitUntil:"networkidle"});
   await assertNoOverflow(mp,"mobile prompt");
   assert.ok(await mp.locator("[data-copy-owner-prompt]").isVisible());
   await mp.screenshot({path:path.join(out,"mobile-owner-prompt.png"),fullPage:true,animations:"disabled"});
  });
  await check("mobile_search_no_horizontal_overflow",async()=>{
   await mp.goto(base+"search/",{waitUntil:"networkidle"});
   await mp.locator(".search-result").first().waitFor();
   await assertNoOverflow(mp,"mobile catalogue");
   await mp.screenshot({path:path.join(out,"mobile-search.png"),fullPage:true,animations:"disabled"});
  });
  await check("fabin_four_workflows_mobile",async()=>{
   await mp.goto(base+'researchers/fabin-gurung/experiments/four-workflows/',{waitUntil:'networkidle'});
   await mp.locator('#building [data-element="S1"]').waitFor();
   for(const name of ['drawings','structure','schedule','estimate','method']){
    await mp.locator('[data-tab="'+name+'"]').click();
    await assertNoOverflow(mp,'Fabin mobile '+name);
   }
   await mp.locator('[data-tab="drawings"]').click();
   await mp.screenshot({path:path.join(out,'fabin-four-workflows-mobile.png'),fullPage:true,animations:'disabled'});
  });
  await check("mobile_wcag_axe",async()=>{
   await mp.goto(base,{waitUntil:"networkidle"});
   const results=await new AxeBuilder({page:mp}).withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();
   const serious=results.violations.filter(v=>v.impact==="critical"||v.impact==="serious");
   fs.writeFileSync(path.join(out,"axe-mobile.json"),JSON.stringify(results.violations,null,2));
   if(serious.length)throw Error("WCAG serious/critical: "+serious.map(x=>x.id+"("+x.nodes.length+")").join(", "));
  });
  await mobile.close();
  const reduced=await browser.newContext({viewport:{width:390,height:844},reducedMotion:"reduce"});
  const rp=await reduced.newPage();
  await check("mobile_320px_navigation",async()=>{
   await rp.goto(base,{waitUntil:"networkidle"});
   await rp.setViewportSize({width:320,height:700});
   await assertNoOverflow(rp,"320px narrow mobile");
   assert.ok(await rp.locator("[data-mobile-menu]").isVisible());
   await rp.screenshot({path:path.join(out,"mobile-320.png"),fullPage:true,animations:"disabled"});
  });
  await check("reduced_motion_disables_animation",async()=>{
   await rp.goto(base,{waitUntil:"networkidle"});
   assert.equal(await rp.locator(".flying-book").evaluate(e=>getComputedStyle(e).animationName),"none");
   assert.equal(await rp.locator("[data-motion-toggle]").isDisabled(),true);
  });
  await reduced.close();
  await check("progressive_navigation_without_javascript",async()=>{
   const nojs=await browser.newContext({viewport:{width:390,height:844},javaScriptEnabled:false});
   const nojsPage=await nojs.newPage();
   await nojsPage.goto(base,{waitUntil:"domcontentloaded"});
   assert.ok(await nojsPage.locator("#site-nav-links").isVisible());
   await assertNoOverflow(nojsPage,"no-JavaScript mobile");
   await nojs.close();
  });
  await check("no_uncaught_javascript_errors",async()=>{assert.deepEqual(javascriptErrors,[])});
 }finally{
  if(browser)await browser.close();
  server.kill("SIGTERM");
  fs.writeFileSync(path.join(out,"results.json"),JSON.stringify({status:failures.length?"FAIL":"PASS",findings,failures},null,2));
 }
 if(failures.length){console.error("BROWSER_QA_FAIL",JSON.stringify(failures));process.exitCode=1}
 else console.log("BROWSER_QA_PASS",findings.length);
}
main().catch(e=>{console.error("BROWSER_QA_FATAL",e);process.exitCode=1});
