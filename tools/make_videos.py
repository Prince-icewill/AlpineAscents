#!/usr/bin/env python3
"""Makes the three short explainer clips for the gallery with PIL + ffmpeg."""
import os, subprocess, shutil, math
from PIL import Image, ImageDraw, ImageFont
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","assets","video"); TMP="/tmp/vf"
W,H,FPS=960,540,24
def font(sz):  # woff2 not readable by PIL, so use system fonts
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p,sz)
    return ImageFont.load_default()
INK=(15,34,51); ICE=(238,245,249); EMB=(232,98,42); GL=(156,196,217); WH=(255,255,255)
def ease(t): return 1-(1-t)**3
def bg():
    im=Image.new("RGB",(W,H),INK); d=ImageDraw.Draw(im)
    for y in range(H):
        k=y/H; d.line([(0,y),(W,y)],fill=(int(15+20*k),int(34+30*k),int(51+40*k)))
    return im,d
def title(d,t,sub=None):
    d.text((48,34),t,font=font(40),fill=WH)
    if sub: d.text((50,86),sub,font=font(20),fill=GL)
def run(name,frames):
    shutil.rmtree(TMP,ignore_errors=True); os.makedirs(TMP)
    for i,fr in enumerate(frames): fr.save(f"{TMP}/f{i:04d}.png")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{TMP}/f%04d.png","-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart","-crf","22",f"{OUT}/{name}.mp4"],check=True)
    frames[min(len(frames)-1,int(FPS*5))].convert("RGB").save(f"{OUT}/{name}.jpg",quality=85)

def altitude():
    pts=[("Sea level",0,100),("Denali base 2,200 m",2200,77),("Kilimanjaro summit 5,895 m",5895,49),("Everest Base Camp 5,364 m",5364,52),("Everest summit 8,849 m",8849,33)]
    pts=[("Sea level",0,100),("Lagos to Jos plateau 1,200 m",1200,89),("Mont Blanc 4,808 m",4808,55),("Everest Base Camp 5,364 m",5364,52),("Everest summit 8,849 m",8849,33)]
    frames=[]; n=FPS*15
    for i in range(n):
        im,d=bg(); title(d,"How thin does the air get?","Oxygen available compared with sea level (%)")
        t=i/n; shown=min(len(pts),1+int(t*len(pts)*1.05))
        for k,(lab,h,pct) in enumerate(pts[:shown]):
            local=min(1,(t*len(pts)*1.05-k)); w=int(ease(max(0,local))*pct/100*620)
            y=150+k*70
            d.text((48,y+4),lab,font=font(20),fill=WH)
            d.rectangle([48,y+34,48+620,y+54],fill=(30,60,85))
            col=EMB if pct<60 else GL
            d.rectangle([48,y+34,48+w,y+54],fill=col)
            if local>0.8: d.text((690,y+26),f"{pct}%",font=font(30),fill=WH)
        frames.append(im)
    return frames

def route():
    camps=[("Base Camp",5364),("Camp 1",6065),("Camp 2",6400),("Camp 3",7200),("Camp 4 (South Col)",7900),("Summit",8849)]
    frames=[]; n=FPS*16
    for i in range(n):
        im,d=bg(); title(d,"Everest, Nepal side","Standard route from Base Camp to the summit")
        t=i/n; prog=ease(min(1,t*1.1))
        base=480; scale=300/(8849-5364)
        xs=[90+k*155 for k in range(len(camps))]
        ys=[base-(h-5364)*scale-20 for _,h in camps]
        d.polygon([(40,520),(40,ys[0]+20)]+[(x,y+20) for x,y in zip(xs,ys)]+[(930,520)],fill=(36,70,98))
        total=len(camps)-1; pos=prog*total; k=min(total-1,int(pos)); f=pos-k
        cx=xs[k]+(xs[k+1]-xs[k])*f; cy=ys[k]+(ys[k+1]-ys[k])*f
        for j,((nm,h),x,y) in enumerate(zip(camps,xs,ys)):
            on=pos>=j-0.01
            d.ellipse([x-7,y-7,x+7,y+7],fill=EMB if on else GL)
            d.text((x-40,y-52),nm,font=font(15),fill=WH if on else GL)
            d.text((x-30,y-32),f"{h:,} m",font=font(14),fill=GL)
        for j in range(total):
            if pos>=j+1: d.line([(xs[j],ys[j]),(xs[j+1],ys[j+1])],fill=EMB,width=4)
        d.line([(xs[k],ys[k]),(cx,cy)],fill=EMB,width=4)
        d.ellipse([cx-11,cy-11,cx+11,cy+11],fill=WH,outline=EMB,width=4)
        frames.append(im)
    return frames

def seven():
    pk=[("Everest",8849),("Aconcagua",6961),("Denali",6190),("Kilimanjaro",5895),("Elbrus",5642),("Vinson",4892),("Puncak Jaya",4884)]
    frames=[]; n=FPS*14
    for i in range(n):
        im,d=bg(); title(d,"The Seven Summits","Highest peak on each continent, drawn to scale")
        t=i/n
        for k,(nm,h) in enumerate(pk):
            local=ease(max(0,min(1,t*2.2-k*0.18)))
            bw=90; x=60+k*128; hh=int(h/8849*320*local); y=510-hh
            d.polygon([(x,510),(x+bw/2,y),(x+bw,510)],fill=(70,110,145) if k else EMB)
            d.polygon([(x+bw/2,y),(x+bw/2-bw*0.11*local,y+hh*0.18),(x+bw/2+bw*0.11*local,y+hh*0.18)],fill=WH)
            if local>0.9:
                d.text((x,y-50),f"{h:,} m",font=font(18),fill=WH); d.text((x,y-26),nm,font=font(15),fill=GL)
        frames.append(im)
    return frames

os.makedirs(OUT,exist_ok=True)
run("altitude",altitude()); run("route",route()); run("sevensummits",seven())
print(os.listdir(OUT))
