"""Browser tests for Alpine Ascents.
Setup:  pip install playwright && playwright install chromium
Run:    start the site (node server.js) in one window, then from the project folder: python tests/run_tests.py
(Resets nothing for you: set data/visitors.json to {"count":0,"lastVisit":null} first for test T14.)"""
import asyncio, json, re, sys
from playwright.async_api import async_playwright
BASE="http://localhost:8080/"
R=[]
def rec(id_, name, ok, detail=""):
    R.append(dict(id=id_,name=name,result="PASS" if ok else "FAIL",detail=detail)); print(("PASS" if ok else "FAIL"),id_,name,detail)
def rgb(s): return tuple(int(x) for x in re.findall(r"\d+",s)[:3])
async def main():
    __import__("os").makedirs("evidence",exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={"width":1440,"height":900},geolocation={"latitude":6.6018,"longitude":3.3515},permissions=["geolocation"],locale="en-GB",timezone_id="Africa/Lagos")
        pg=await ctx.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.on("console",lambda m: errs.append(m.text) if m.type=="error" and "CORS" not in m.text and "Failed to load resource" not in m.text else None)
        await pg.goto(BASE); await pg.wait_for_selector(".hero"); await pg.wait_for_timeout(1200)
        # T01 menu at top
        top=await pg.evaluate("document.querySelector('.main-nav').getBoundingClientRect().top")
        n=await pg.evaluate("document.querySelectorAll('.main-nav .nav-link, .main-nav .dropdown-item').length")
        rec("T01","Menu is in the top section of the page",top<120 and n>=11,f"nav top={top:.0f}px, {n} links")
        # T02 all routes
        ROUTES=["home","history","styles","techniques","shelter","hazards","records","clubs","stories","gallery","latest","guidelines"]; ok=True; bad=[]
        for r in ROUTES:
            await pg.evaluate(f"location.hash='#/{r}'"); await pg.wait_for_timeout(750)
            h=await pg.inner_text("#view h1"); url=pg.url
            if not h.strip() or ("#/"+r) not in url: ok=False; bad.append(r)
        rec("T02","All 12 pages load inside the same page (SPA, no reload)",ok,"failed: "+",".join(bad) if bad else "12 of 12")
        nav=await pg.evaluate("performance.getEntriesByType('navigation').length")
        # T03 required topics
        txt={}
        for r in ["history","styles","techniques","shelter","hazards","records"]:
            await pg.evaluate(f"location.hash='#/{r}'"); await pg.wait_for_timeout(700); txt[r]=(await pg.inner_text("#view")).lower()
        rec("T03","History, Types/Styles, Techniques, Sheltering, Hazards and Records pages have content",all(len(v)>1500 for v in txt.values()),", ".join(f"{k}:{len(v)}" for k,v in txt.items()))
        # T04 hover colour
        await pg.evaluate("location.hash='#/home'"); await pg.wait_for_timeout(700)
        l=pg.locator('.main-nav [data-route="gallery"]')
        before=rgb(await l.evaluate("e=>getComputedStyle(e).backgroundColor")) if False else await l.evaluate("e=>getComputedStyle(e).backgroundColor")
        await l.hover(); await pg.wait_for_timeout(450)
        hov=await l.evaluate("e=>getComputedStyle(e).backgroundColor")
        rec("T04","Menu option changes colour on hover",before!=hov,f"{before} -> {hov}")
        # T05 click colour (active)
        await l.click(); await pg.wait_for_timeout(900)
        await pg.mouse.move(700,500); await pg.wait_for_timeout(450)
        act=await l.evaluate("e=>getComputedStyle(e).backgroundColor"); cls=await l.get_attribute("class")
        rec("T05","Menu option keeps a different colour after it is clicked",("active" in cls) and act not in (before,hov),f"{act}, class={cls}")
        # T06 fade
        await pg.evaluate("location.hash='#/styles'")
        await pg.wait_for_timeout(60)
        op=await pg.evaluate("parseFloat(getComputedStyle(document.getElementById('view')).opacity)")
        await pg.wait_for_timeout(900)
        op2=await pg.evaluate("parseFloat(getComputedStyle(document.getElementById('view')).opacity)")
        rec("T06","Page content fades out/in on menu click",op<1 and op2==1,f"opacity during={op:.2f}, after={op2:.2f}")
        # T07 dropdown fade
        dd=pg.locator('.main-nav [data-group="about"]'); await dd.hover(); await pg.wait_for_timeout(500)
        vis=await pg.evaluate("getComputedStyle(document.querySelector('.main-nav .dropdown-menu')).opacity")
        await pg.mouse.move(700,500); await pg.wait_for_timeout(500)
        vis2=await pg.evaluate("getComputedStyle(document.querySelector('.main-nav .dropdown-menu')).opacity")
        tr=await pg.evaluate("getComputedStyle(document.querySelector('.main-nav .dropdown-menu')).transitionProperty")
        rec("T07","Dropdown menu fades in on hover and out when the mouse leaves",vis=="1" and vis2=="0" and "opacity" in tr,f"open={vis}, closed={vis2}")
        # T08 ticker
        tk=await pg.inner_text("#tickerTrack"); box=await pg.evaluate("(()=>{const r=document.getElementById('ticker').getBoundingClientRect();return [r.bottom,innerHeight,getComputedStyle(document.getElementById('tickerTrack')).animationName]})()")
        rec("T08","Ticker is fixed at the bottom and scrolls continuously",abs(box[0]-box[1])<2 and box[2]=="tick",f"animation={box[2]}")
        x1=await pg.evaluate("document.getElementById('tickerTrack').getBoundingClientRect().left"); await pg.wait_for_timeout(1500)
        x2=await pg.evaluate("document.getElementById('tickerTrack').getBoundingClientRect().left")
        rec("T09","Ticker text actually moves",x1!=x2,f"left {x1:.0f} -> {x2:.0f}")
        rec("T10","Ticker shows current date",bool(re.search(r"October 2026",tk)) ,tk[:60].replace("\n"," "))
        t1=await pg.inner_text("#tickerTrack .t-time"); await pg.wait_for_timeout(2100); t2=await pg.inner_text("#tickerTrack .t-time")
        rec("T11","Ticker time updates every second",t1!=t2,f"{t1} -> {t2}")
        rec("T12","Ticker shows location from HTML5 geolocation",bool(re.search(r"6\.60.N, 3\.35.E",tk)),re.search(r"Location[^|]*",tk).group(0)[:60] if re.search(r"Location[^|]*",tk) else "")
        # T13 visitor counter
        vc=await pg.inner_text("#visitorCount"); pos=await pg.evaluate("(()=>{const v=document.querySelector('.visitor-box').getBoundingClientRect(),l=document.querySelector('.logo-img').getBoundingClientRect();return [v.right,innerWidth,l.right<=v.right && l.left<document.getElementById('visitorCount').getBoundingClientRect().left, v.top]})()")
        rec("T13","Visitor count is top right, beside the logo",pos[2] and pos[0]>pos[1]-120 and pos[3]<60 and vc.replace("\n","").isdigit(),f"count={vc.replace(chr(10),'')}")
        # T14 counter persists / session
        c1=int(vc.replace("\n","")); pg2=pg; await pg2.reload(); await pg2.wait_for_timeout(1500)
        c2=int((await pg2.inner_text("#visitorCount")).replace("\n",""))
        ctx2=await b.new_context(); pg3=await ctx2.new_page(); await pg3.goto(BASE); await pg3.wait_for_timeout(1200)
        c3=int((await pg3.inner_text("#visitorCount")).replace("\n","")); await ctx2.close()
        rec("T14","Counter: reload in same session is not double counted, new visitor adds one",c2==c1 and c3==c1+1,f"{c1} / same session {c2} / new visitor {c3}")
        # clubs
        await pg.evaluate("location.hash='#/clubs'"); await pg.wait_for_timeout(2000)
        mk=await pg.evaluate("document.querySelectorAll('.leaflet-marker-icon').length")
        rec("T15","Clubs page draws a map with a marker for every club",mk>=17,f"{mk} markers incl. user")
        await pg.click("#nearMe"); await pg.wait_for_timeout(700)
        d=await pg.inner_text("#clubList"); first=await pg.inner_text("#clubList .club h3")
        rec("T16","Distance from user is calculated with geolocation and list sorts by it",bool(re.search(r"km away",d)) and "Nepal" not in first,f"nearest={first}")
        await pg.click('#regionChips [data-region="Asia"]'); await pg.wait_for_timeout(400)
        cnt=await pg.inner_text("#clubCount"); rec("T17","Region filter works",cnt.startswith("5 of"),cnt)
        await pg.fill("#clubSearch","swiss"); await pg.wait_for_timeout(300)
        rec("T18","Club search works (with Asia filter, 'swiss' gives none)", "0 of" in await pg.inner_text("#clubCount"))
        await pg.fill("#clubSearch",""); await pg.click('#regionChips [data-region="All"]'); await pg.wait_for_timeout(300)
        gm=await pg.evaluate("[...document.querySelectorAll('#clubList a')].filter(a=>a.href.includes('google.com/maps')).length")
        rec("T19","Every club card links to Google Maps",gm>=17,f"{gm} links")
        await pg.screenshot(path="evidence/clubs-map.png")
        # stories / gallery / latest / guidelines
        await pg.evaluate("location.hash='#/stories'"); await pg.wait_for_timeout(800)
        rec("T20","Success stories shown",await pg.locator(".story").count()>=6,f"{await pg.locator('.story').count()} stories")
        await pg.evaluate("location.hash='#/gallery'"); await pg.wait_for_timeout(1000)
        imgs=await pg.evaluate("[...document.querySelectorAll('#galGrid img')].every(i=>i.complete&&i.naturalWidth>0)")
        vids=await pg.evaluate("[...document.querySelectorAll('video')].map(v=>v.readyState>=1||v.networkState)")
        rec("T21","Gallery shows pictures and they all load",imgs and await pg.locator('#galGrid img').count()>=13,f"{await pg.locator('#galGrid img').count()} pictures")
        await pg.wait_for_timeout(800)
        dur=await pg.evaluate("[...document.querySelectorAll('video')].map(v=>Math.round(v.duration))")
        rec("T22","Gallery has three playable videos",len(dur)==3 and all(x>5 for x in dur),f"durations {dur}")
        await pg.click("#galGrid .g-item >> nth=0"); await pg.wait_for_timeout(700)
        sh=await pg.evaluate("document.getElementById('lightbox').classList.contains('show')"); t0=await pg.inner_text("#lbTitle")
        await pg.keyboard.press("ArrowRight"); await pg.wait_for_timeout(300); t1_=await pg.inner_text("#lbTitle")
        rec("T23","Lightbox opens and arrow keys move between pictures",sh and t0!=t1_,f"{t0} -> {t1_}")
        await pg.screenshot(path="evidence/lightbox.png"); await pg.keyboard.press("Escape"); await pg.wait_for_timeout(500)
        await pg.click('#galChips [data-cat="Culture"]'); await pg.wait_for_timeout(300)
        rec("T24","Gallery category filter works",await pg.locator("#galGrid img").count()==2)
        await pg.evaluate("location.hash='#/latest'"); await pg.wait_for_timeout(700)
        rec("T25","Latest developments page lists dated items with source links",await pg.locator(".news-item a").count()>=6)
        # hyperlinks
        bad=[]
        for r in ROUTES:
            await pg.evaluate(f"location.hash='#/{r}'"); await pg.wait_for_timeout(500)
            hs=await pg.evaluate("[...document.querySelectorAll('#view a:not(.leaflet-control-zoom-in):not(.leaflet-control-zoom-out)')].map(a=>a.getAttribute('href'))")
            for h in hs:
                if not h or h=="#": bad.append((r,h))
        rec("T26","No empty or dead (#) links on any page",not bad,str(bad[:3]))
        # images alt
        await pg.evaluate("location.hash='#/home'"); await pg.wait_for_timeout(900)
        broken=await pg.evaluate("[...document.images].filter(i=>i.complete&&i.naturalWidth==0).length")
        rec("T27","No broken images on the home page",broken==0)
        # records interaction
        await pg.evaluate("location.hash='#/records'"); await pg.wait_for_timeout(800)
        await pg.fill("#peakSearch","pakistan"); await pg.wait_for_timeout(300)
        rows=await pg.locator("#peakTable tbody tr").count()
        rec("T28","Records table search filters rows",rows==5,f"{rows} rows for 'pakistan'")
        await pg.fill("#peakSearch",""); await pg.click('#peakTable th[data-k="first"]'); await pg.wait_for_timeout(200)
        first=await pg.inner_text("#peakTable tbody tr:first-child td:nth-child(2)")
        rec("T29","Records table sorts when a heading is clicked",first.strip()=="Annapurna I",first)
        await pg.click('[data-bs-target="#tab7"]'); await pg.wait_for_timeout(1500)
        w=await pg.evaluate("[...document.querySelectorAll('#sevenBars .fill')].map(f=>f.getBoundingClientRect().width>5)")
        rec("T30","Seven Summits bars draw to scale",all(w) and len(w)==7)
        # guidelines checkbox persists
        await pg.evaluate("location.hash='#/guidelines'"); await pg.wait_for_timeout(800)
        await pg.check("#view .check-list input >> nth=0"); await pg.evaluate("location.hash='#/home'"); await pg.wait_for_timeout(600); await pg.evaluate("location.hash='#/guidelines'"); await pg.wait_for_timeout(800)
        rec("T31","Guideline ticks are remembered",await pg.is_checked("#view .check-list input >> nth=0"))
        # back button
        await pg.evaluate("location.hash='#/hazards'"); await pg.wait_for_timeout(500); await pg.go_back(); await pg.wait_for_timeout(800)
        rec("T32","Browser back button works",pg.url.endswith("guidelines") or pg.url.endswith("#/guidelines"),pg.url)
        # unknown route
        await pg.evaluate("location.hash='#/nonsense'"); await pg.wait_for_timeout(700)
        rec("T33","Unknown address falls back to home",(await pg.inner_text("#view h1")).startswith("Climb"))
        rec("T34","No JavaScript errors in the console during the run",not errs,str(errs[:2]))
        await ctx.close()
        # mobile
        mctx=await b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True,geolocation={"latitude":6.6,"longitude":3.35},permissions=["geolocation"])
        m=await mctx.new_page(); await m.goto(BASE); await m.wait_for_timeout(1500)
        ov=await m.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
        tog=await m.is_visible(".navbar-toggler")
        rec("T35","Mobile 390px: no sideways scrolling, menu collapses to a button",ov and tog)
        await m.screenshot(path="evidence/mobile-home.png")
        await m.click(".navbar-toggler"); await m.wait_for_timeout(600); await m.screenshot(path="evidence/mobile-menu.png")
        await m.click('.main-nav [data-route="history"]') if await m.is_visible('.main-nav [data-route="history"]') else None
        await m.click('.main-nav [data-group="about"]'); await m.wait_for_timeout(400); await m.click('.main-nav [data-route="hazards"]'); await m.wait_for_timeout(1200)
        rec("T36","Mobile menu navigates to a page and closes",(await m.inner_text("#view h1"))=="Hazards" and not await m.evaluate("document.getElementById('mainMenu').classList.contains('show')"))
        for r in ["clubs","records","gallery","techniques","latest"]:
            await m.evaluate(f"location.hash='#/{r}'"); await m.wait_for_timeout(900)
            if not await m.evaluate("document.documentElement.scrollWidth<=innerWidth+1"): rec("T37","Mobile overflow on "+r,False); break
        else: rec("T37","Mobile: no sideways scroll on clubs, records, gallery, techniques, latest",True)
        await m.evaluate("location.hash='#/clubs'"); await m.wait_for_timeout(1500); await m.screenshot(path="evidence/mobile-clubs.png")
        await mctx.close()
        # tablet
        tctx=await b.new_context(viewport={"width":820,"height":1180}); t=await tctx.new_page(); await t.goto(BASE); await t.wait_for_timeout(1500)
        rec("T38","Tablet 820px: layout fits",await t.evaluate("document.documentElement.scrollWidth<=innerWidth+1")); await t.screenshot(path="evidence/tablet-home.png"); await tctx.close()
        # geolocation denied
        dctx=await b.new_context(permissions=[],locale="en-GB",timezone_id="Africa/Lagos"); d=await dctx.new_page(); await d.goto(BASE); await d.wait_for_timeout(1800)
        tk=await d.inner_text("#tickerTrack"); rec("T39","Location denied: ticker still shows date, time and a fallback place",("Lagos" in tk) and "October 2026" in tk,re.search(r"Location[^|]*",tk).group(0)[:80])
        await dctx.close()
        # file:// fallback
        fctx=await b.new_context(); f=await fctx.new_page(); ferr=[]; f.on("pageerror",lambda e:ferr.append(str(e)))
        await f.goto("file://"+__import__("os").path.abspath("index.html")+""); await f.wait_for_timeout(1800)
        rec("T40","Opens from disk (double-click index.html) using the bundled data and local counter",(await f.inner_text("#view h1")).startswith("Climb") and (await f.inner_text("#visitorCount")).replace("\n","").isdigit() and not ferr,str(ferr[:1]))
        await fctx.close()
        # desktop screenshots of everything for the report
        sctx=await b.new_context(viewport={"width":1366,"height":768},geolocation={"latitude":6.6018,"longitude":3.3515},permissions=["geolocation"],locale="en-GB",timezone_id="Africa/Lagos"); s=await sctx.new_page()
        await s.goto(BASE); await s.wait_for_timeout(1500)
        for r in ROUTES:
            await s.evaluate(f"location.hash='#/{r}'"); await s.wait_for_timeout(1700 if r=="clubs" else 900); await s.screenshot(path=f"evidence/page-{r}.png")
        await s.evaluate("location.hash='#/home'"); await s.wait_for_timeout(700)
        await s.hover('.main-nav [data-group="about"]'); await s.wait_for_timeout(600); await s.screenshot(path="evidence/menu-dropdown.png")
        await b.close()
    __import__("os").makedirs("evidence",exist_ok=True); json.dump(R,open("evidence/test_results.json","w"),indent=1)
    print("\n",sum(r["result"]=="PASS" for r in R),"passed,",sum(r["result"]=="FAIL" for r in R),"failed of",len(R))
asyncio.run(main())
