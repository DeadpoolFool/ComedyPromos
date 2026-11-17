# Host credit for Full Circle 11/22: Felipe Calle, bigger photo + name. Fonts: @fontsource anton + space-mono woff in fonts/.
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC='full-circle-nov-22/original_story.png'
im=Image.open(SRC).convert('RGB'); W,H=im.size
RED=(223,39,49); CREAM=(239,230,210); BLACK=(0,0,0)
UP=30; DOWN=12
out=Image.new('RGB',(W,H),BLACK)
out.paste(im.crop((0,0,W,400)),(0,0))                 # label + title untouched
out.paste(im.crop((0,420,W,1556)),(0,420-UP))          # headliner + 3 comics, nudged up
out.paste(im.crop((0,1698,W,H-DOWN)),(0,1698+DOWN))    # date bar + footer, nudged down
bar_top=1700+DOWN
# Host photo: Felipe Calle headshot, face crop, warm B&W to match the other circles
from PIL import ImageOps
import numpy as np
src=Image.open('full-circle-nov-22/felipe_calle_source.jpeg').convert('RGB')
CX,CY,SZ=1060,640,860
ph=src.crop((CX-SZ//2,CY-SZ//2,CX+SZ//2,CY+SZ//2))
a=np.asarray(ph).astype(float)
lum=0.6*a[...,0]+0.35*a[...,1]+0.05*a[...,2]   # red-weighted so the blue wall goes dark grey
lum=np.clip((lum-20)/(235-20),0,1)**1.05
lo=np.array([10,10,10]);hi=np.array([239,230,210])
duo=(lo+(hi-lo)*lum[...,None]).astype('uint8')
ph=Image.fromarray(duo)
R=82; RING=4; GAP=6; rp=R-RING-GAP
ph=ph.resize((2*rp,2*rp),Image.LANCZOS).filter(ImageFilter.UnsharpMask(1,40,2))
S=4
mask=Image.new('L',(2*rp*S,2*rp*S),0); ImageDraw.Draw(mask).ellipse((0,0,2*rp*S-1,2*rp*S-1),255)
mask=mask.resize((2*rp,2*rp),Image.LANCZOS)
ring=Image.new('L',(2*R*S,2*R*S),0); d=ImageDraw.Draw(ring)
d.ellipse((0,0,2*R*S-1,2*R*S-1),255); d.ellipse((RING*S,RING*S,(2*R-RING)*S-1,(2*R-RING)*S-1),0)
ring=ring.resize((2*R,2*R),Image.LANCZOS)
# text
F='fonts/'
mono=ImageFont.truetype(F+'fontsource-space-mono-5.3.0/files/space-mono-latin-700-normal.woff',27)
NAME='FELIPE CALLE'
anton=ImageFont.truetype(F+'fontsource-anton-5.3.0/files/anton-latin-400-normal.woff',72)
def spaced(draw,xy,text,font,fill,track):
    x,y=xy
    for ch in text:
        draw.text((x,y),ch,font=font,fill=fill); x+=draw.textlength(ch,font=font)+track
    return x-track
tmp=ImageDraw.Draw(Image.new('RGB',(10,10)))
track=6
hb_w=sum(tmp.textlength(c,font=mono) for c in 'HOSTED BY')+track*8
ph_bb=tmp.textbbox((0,0),NAME,font=anton); ph_w=ph_bb[2]-ph_bb[0]
text_w=max(hb_w,ph_w); GAPX=30
group=2*R+GAPX+text_w
x0=int(round((W-group)/2))
zone_top=1556-UP; cyN=(zone_top+bar_top)//2
top=cyN-R
out.paste(BLACK,(x0,top,x0+2*R,top+2*R))
out.paste(Image.new('RGB',(2*R,2*R),RED),(x0,top),ring)
out.paste(ph,(x0+R-rp,top+R-rp),mask)
d=ImageDraw.Draw(out)
hb_bb=tmp.textbbox((0,0),'H',font=mono); hb_h=hb_bb[3]-hb_bb[1]
ph_h=ph_bb[3]-ph_bb[1]; LG=16
block_h=hb_h+LG+ph_h; ty=cyN-block_h//2
tx=x0+2*R+GAPX
spaced(d,(tx,ty-hb_bb[1]),'HOSTED BY',mono,RED,track)
d.text((tx-ph_bb[0],ty+hb_h+LG-ph_bb[1]),NAME,font=anton,fill=CREAM)
out.save('full-circle-nov-22/full_circle_story_1080x1920.png')
print('circle',top,top+2*R,'bar',bar_top,'group x',x0,x0+group,'names end',1545-UP)
