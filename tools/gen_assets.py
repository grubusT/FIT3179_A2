import math, random
OUT='assets/'  # run from the repo root
random.seed(7)
def ridge(w,h,base,amp,n,seed,rough=0.35):
    r=random.Random(seed); pts=[]
    # smooth ridge = sum of sines + small noise, sampled
    ph=[r.random()*6.28 for _ in range(4)]; fr=[1,2.3,4.1,9.7]; am=[1,0.45,0.22,0.07]
    for i in range(n+1):
        x=w*i/n; t=x/w*math.pi*2
        y=base-amp*sum(a*math.sin(f*t+p) for a,f,p in zip(am,fr,ph))/1.74
        y+=r.uniform(-1,1)*amp*0.03*rough
        pts.append((x,y))
    d=f"M0,{h} L"+" L".join(f"{x:.1f},{y:.1f}" for x,y in pts)+f" L{w},{h} Z"
    return d
def tree(x,y,s,r):
    # eucalypt: tall leaning trunk, forked limbs, sparse clumped canopy
    lean=r.uniform(-8,8)*s; top=y-86*s; tx=x+lean
    g=[f'<path d="M{x-2.6*s:.1f},{y} C{x-2*s:.1f},{y-40*s:.1f} {tx-1.2*s:.1f},{y-62*s:.1f} {tx-0.6*s:.1f},{top:.1f} L{tx+1.4*s:.1f},{top:.1f} C{tx+1.6*s:.1f},{y-60*s:.1f} {x+2.2*s:.1f},{y-38*s:.1f} {x+3*s:.1f},{y} Z"/>']
    ends=[]
    for k in range(r.randint(3,5)):
        ex=tx+r.uniform(-34,34)*s; ey=top-r.uniform(4,30)*s
        bx=tx+r.uniform(-4,4)*s; by=top+r.uniform(-4,20)*s
        g.append(f'<path d="M{bx:.1f},{by:.1f} Q{(bx+ex)/2:.1f},{by-6*s:.1f} {ex:.1f},{ey:.1f}" stroke="currentColor" stroke-width="{1.3*s:.1f}" stroke-linecap="round" fill="none"/>')
        ends.append((ex,ey))
    for ex,ey in ends:
        for _ in range(r.randint(5,8)):
            g.append(f'<ellipse cx="{ex+r.uniform(-11,11)*s:.1f}" cy="{ey+r.uniform(-6,4)*s:.1f}" rx="{r.uniform(3.5,7.5)*s:.1f}" ry="{r.uniform(2,4)*s:.1f}" transform="rotate({r.uniform(-20,20):.0f} {ex:.1f} {ey:.1f})"/>')
    return '\n'.join(g)
W,H=1600,700
layers=[("var(--l1)",430,70,1),("var(--l2)",480,60,2),("var(--l3)",540,55,3),("var(--l4)",610,40,4)]
svg=[f'<svg class="hero-scene" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">',
 '<defs><radialGradient id="glow"><stop offset="0" stop-color="#fff4d6" stop-opacity=".9"/><stop offset="1" stop-color="#fff4d6" stop-opacity="0"/></radialGradient></defs>',
 '<g class="sun"><circle cx="1130" cy="330" r="230" fill="url(#glow)"/><circle cx="1130" cy="330" r="70" fill="var(--sun)"/></g>']
for i,(c,b,a,s) in enumerate(layers):
    svg.append(f'<path class="layer layer-{i+1}" d="{ridge(W,H,b,a,120,s)}" fill="{c}"/>')
    if i==2:
        r=random.Random(11); svg.append('<g class="layer layer-3 trees far" fill="var(--l3)" color="var(--l3)">')
        for x in [140,190,860,905,1380,1420,1460]: svg.append(tree(x,b+12+r.uniform(-8,8),0.55,r))
        svg.append('</g>')
r=random.Random(3)
svg.append('<g class="layer layer-4 trees near" fill="var(--l4)" color="var(--l4)">')
for x,s in [(60,1.5),(250,1.15),(1290,1.25),(1520,1.7),(1450,1.0)]: svg.append(tree(x,700,s*1.8,r))
svg.append('</g></svg>')
open(OUT+'hero.svg.html','w').write('\n'.join(svg))
# ridge dividers (top edge of a coloured band)
for name,seed in [('ridge-a',21),('ridge-b',33)]:
    d=ridge(1600,120,60,40,90,seed)
    open(OUT+name+'.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 120" preserveAspectRatio="none"><path d="{d}" fill="#000"/></svg>')
# topographic contour texture (tileable-ish; used at low opacity)
paths=[]; r=random.Random(5)
for cx,cy in [(120,140),(420,330),(260,520),(560,90),(600,560)]:
    ph=[r.random()*6.28 for _ in range(3)]
    for k in range(1,9):
        R=k*22; pts=[]
        for j in range(73):
            t=j/72*2*math.pi
            rr=R*(1+0.18*math.sin(3*t+ph[0])+0.09*math.sin(5*t+ph[1]+k*0.2)+0.05*math.sin(7*t+ph[2]))
            pts.append(f"{cx+rr*math.cos(t):.1f},{cy+rr*0.8*math.sin(t):.1f}")
        paths.append('M'+' L'.join(pts)+'Z')
open(OUT+'contours.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640" viewBox="0 0 640 640"><path d="'+' '.join(paths)+'" fill="none" stroke="#3f5f4a" stroke-width="1"/></svg>')
print('ok')
# Treeline that stands on the takeaway ridge (bookends the hero)
r=random.Random(4)
t=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 260" fill="#1f3b2d" color="#1f3b2d">']
for x,s in [(80,1.25),(230,1.9),(330,1.35),(450,1.6)]: t.append(tree(x,262,s*1.15,r))
t.append('</svg>')
open(OUT+'treeline.svg','w').write('\n'.join(t))
