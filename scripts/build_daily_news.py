#!/usr/bin/env python3
"""Build source-led daily news episodes from RSS feeds.

This first production milestone intentionally uses animated editorial graphics,
not unlicensed broadcast footage. RSS headline/description text is attributed.
It refuses to invent missing story details.
"""
from __future__ import annotations
import argparse, html, json, os, re, subprocess, sys, time, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from email.utils import parsedate_to_datetime

import requests
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
OUT = Path("output")
FEEDS = {
 "india": [
  "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
  "https://www.thehindu.com/news/national/feeder/default.rss",
  "https://indianexpress.com/section/india/feed/",
 ],
 "global": [
  "https://feeds.bbci.co.uk/news/world/rss.xml",
  "https://www.theguardian.com/world/rss",
  "https://www.npr.org/rss/rss.php?id=1004",
 ],
}

def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()

def fetch_feed(url, region):
    try:
        r = requests.get(url, timeout=25, headers={"User-Agent":"NewsStudio/1.0 (RSS reader)"})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = root.findall(".//item")
        found=[]
        for item in items:
            title=clean(item.findtext("title"))
            desc=clean(item.findtext("description"))
            link=clean(item.findtext("link"))
            pub=clean(item.findtext("pubDate"))
            if not title or not link: continue
            try: dt=parsedate_to_datetime(pub).astimezone(timezone.utc)
            except Exception: dt=None
            if dt and (datetime.now(timezone.utc)-dt).total_seconds()>36*3600: continue
            found.append({"title":title,"description":desc,"url":link,"published":pub,"feed":url})
        return found
    except Exception as e:
        print(f"Feed unavailable ({url}): {e}", file=sys.stderr)
        return []

def gather(region):
    all_items=[]
    for feed in FEEDS[region]: all_items.extend(fetch_feed(feed,region))
    unique={}
    for x in all_items:
        key=re.sub(r"[^a-z0-9]","",x["title"].lower())
        if key and key not in unique: unique[key]=x
    # Keep publisher diversity and avoid repeating near-identical headlines.
    items=sorted(unique.values(), key=lambda x: x.get("published",""), reverse=True)
    return items[:8]

def font(size,bold=False):
    paths=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in paths:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def wrap(draw,text,f,maxw):
    words=text.split(); lines=[]; line=""
    for word in words:
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=f)[2] <= maxw: line=test
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def make_card(region, index, total, item, label, stamp, path):
    im=Image.new("RGB",(W,H),(8,17,34)); d=ImageDraw.Draw(im)
    # editorial grid and gradient-like bands
    for y in range(H):
        c=int(8+13*y/H); d.line((0,y,W,y),fill=(5,c,30+c//2))
    d.rectangle((0,0,W,18),fill=(225,42,55) if region=="india" else (48,116,220))
    d.text((110,90), "NEWS DESK  /  "+label.upper(),font=font(34,True),fill=(255,255,255))
    d.text((110,160), f"{index:02d}  /  {total:02d}",font=font(28),fill=(150,180,210))
    d.line((110,225,1810,225),fill=(60,85,115),width=3)
    title_lines=wrap(d,item["title"],font(72,True),1660)
    y=310
    for line in title_lines[:5]:
        d.text((110,y),line,font=font(72,True),fill=(255,255,255)); y+=100
    desc=item.get("description") or "The linked report contains the full details. This bulletin reports the published headline and source without adding unverified claims."
    desc_lines=wrap(d,desc,font(38),1600)
    y=max(y+55,690)
    for line in desc_lines[:5]:
        d.text((115,y),line,font=font(38),fill=(195,211,230)); y+=57
    d.rectangle((110,930,1810,1010),fill=(18,35,59))
    publisher=urllib.parse.urlparse(item["url"]).netloc.replace("www.","")
    d.text((140,950),f"SOURCE  {publisher}   •   {stamp}",font=font(25,True),fill=(190,210,230))
    im.save(path,quality=92)

def run(cmd):
    subprocess.run(cmd,check=True)

def render(region, items, date):
    if len(items)<5: raise RuntimeError(f"Only {len(items)} current RSS stories found for {region}; refusing to publish a thin bulletin.")
    work=OUT/region; work.mkdir(parents=True,exist_ok=True)
    # 8 stories + opener + close; narration is source text only, no invented analysis.
    script=[]; cards=[]
    opener=f"Here is your {('India' if region=='india' else 'global')} news briefing for {date}. We have selected {len(items)} recent reports. Each headline is attributed to its publisher."
    script.append(("OPENING",opener))
    for i,item in enumerate(items,1):
        publisher=urllib.parse.urlparse(item["url"]).netloc.replace("www.","")
        text=f"Story {i}. {item['title']}. "
        if item.get("description"): text+=item["description"]+" "
        text+=f"Source: {publisher}. Read the original report using the source link in the episode description."
        script.append((item["title"],text))
    script.append(("CLOSING","That is the briefing. Check the linked original reports for updates and developing details."))
    # eSpeak voice clips; each story card remains visible while its narration plays.
    segments=[]; srt=[]; cursor=0.0
    for i,(heading,narration) in enumerate(script):
        wav=work/f"voice_{i:02d}.wav"
        run(["espeak-ng","-v","en-us","-s","155","-w",str(wav),narration])
        probe=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(wav)],text=True)
        dur=float(probe.strip())
        # 3-minute target: allocate natural narration first; add a paced visual hold to hit 180s.
        image=work/f"card_{i:02d}.jpg"
        if i==0: card={"title":f"{region.upper()} NEWS BRIEFING","description":f"Top {len(items)} reports • {date}","url":items[0]["url"]}
        elif i==len(script)-1: card={"title":"END OF BRIEFING","description":"Sources are listed in the accompanying description.","url":items[-1]["url"]}
        else: card=items[i-1]
        make_card(region,i+1,len(script),card,region,date,image)
        segments.append((wav,image,dur))
    total_voice=sum(x[2] for x in segments)
    if total_voice>178: raise RuntimeError(f"Narration is {total_voice:.1f}s; exceeds 3-minute target. Reduce story count/description length.")
    hold=(180-total_voice)/len(segments)
    concat=[]
    for i,(wav,img,dur) in enumerate(segments):
        seg=work/f"segment_{i:02d}.mp4"
        segdur=dur+hold
        run(["ffmpeg","-y","-loop","1","-i",str(img),"-i",str(wav),"-vf","scale=1920:1080,zoompan=z='min(zoom+0.0005,1.04)':d=1:s=1920x1080:fps=24,format=yuv420p","-af","apad","-t",f"{segdur:.3f}","-r","24","-c:v","libx264","-preset","veryfast","-crf","21","-c:a","aac","-b:a","160k","-shortest",str(seg)])
        concat.append(seg)
    listfile=work/"concat.txt"
    listfile.write_text("".join(f"file '{p.resolve()}'\n" for p in concat), encoding="utf-8")
    final=OUT/f"{region}-news-{date}.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(listfile),"-c","copy","-movflags","+faststart",str(final)])
    # Create complete source list and YouTube metadata.
    (OUT/f"{region}-sources-{date}.txt").write_text("\n".join(f"{x['title']}\n{x['url']}\n" for x in items), encoding="utf-8")
    (OUT/f"{region}-description-{date}.txt").write_text(f"{region.title()} news briefing — {date}\n\nSources and original reporting:\n"+"\n".join(f"- {x['title']} — {x['url']}" for x in items)+"\n\nThis video summarizes publisher-provided RSS headlines and descriptions. Check original reports for updates.", encoding="utf-8")
    actual=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(final)],text=True).strip())
    if not 175<=actual<=185: raise RuntimeError(f"Final video duration {actual:.1f}s is outside 3-minute QC window.")
    return str(final)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--region",choices=["india","global","both"],default="both"); args=ap.parse_args()
    OUT.mkdir(exist_ok=True); date=datetime.now().strftime("%Y-%m-%d")
    results={}
    for region in (["india","global"] if args.region=="both" else [args.region]):
        items=gather(region)
        if len(items)<5: raise RuntimeError(f"Insufficient fresh source items for {region}: {len(items)}")
        results[region]=render(region,items,date)
    (OUT/"daily_manifest.json").write_text(json.dumps({"date":date,"videos":results},indent=2))
    print(json.dumps(results,indent=2))
if __name__=="__main__": main()
