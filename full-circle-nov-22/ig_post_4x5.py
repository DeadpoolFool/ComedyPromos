from PIL import Image
import numpy as np
S=Image.open('full-circle-nov-22/full_circle_story_1080x1920.png').convert('RGB')
W=1080;H=1350
a=np.array(S).astype(int); nb=(a.sum(2)>60).any(1)
def strip(y0,y1,x0=0,x1=W):
    # tighten to content rows
    return S.crop((x0,y0,x1,y1))
def bbox(y0,y1):
    sub=np.array(S.crop((0,y0,W,y1))).astype(int); m=sub.sum(2)>60
    ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]
    return S.crop((xs.min(),y0+ys.min(),xs.max()+1,y0+ys.max()+1))
parts=[('label',bbox(60,110),1.0,0),
       ('title',bbox(160,390),0.82,18),
       ('head',bbox(400,960),0.55,22),
       ('hname',bbox(970,1110),0.80,10),
       ('comics',bbox(1120,1520),0.68,20),
       ('host',bbox(1525,1705),0.78,18)]
out=Image.new('RGB',(W,H),(0,0,0))
y=40
for name,im,sc,gap in parts:
    y+=gap+5
    im=im.resize((round(im.width*sc),round(im.height*sc)),Image.LANCZOS)
    x=(W-im.width)//2 if name!='label' else (W-round(bbox(160,390).width*0.82))//2
    out.paste(im,(x,y)); print(name,y,y+im.height); y+=im.height
# bottom: date bar + footer full width from story (bar 1712..1811, footer to 1910)
bar=S.crop((0,1712,W,1812)); foot=S.crop((0,1820,W,1905))
fy=H-foot.height-6; by=fy-bar.height-8
print('bar',by,'free gap above bar',by-y)
out.paste(bar,(0,by)); out.paste(foot,(0,fy))
out.save('full-circle-nov-22/full_circle_post_1080x1350.png')
