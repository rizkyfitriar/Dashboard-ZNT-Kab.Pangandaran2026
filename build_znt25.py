"""Bangun znt25_geo.js dari shapefile ZNT tahun lalu + nilai pembanding per zona 2026.
Pakai: python build_znt25.py  (butuh shapefile, pyproj, shapely; baca data_mentah/ZNT2025/ZONA_LAYER.shp)"""
import json,shapefile,collections
from shapely.geometry import shape,mapping
from shapely import make_valid,coverage_simplify,STRtree
from shapely.ops import transform
from pyproj import CRS,Transformer
import sys
SRC=sys.argv[1] if len(sys.argv)>1 else 'data_mentah/ZNT2025/ZONA_LAYER'
r=shapefile.Reader(SRC);t=Transformer.from_crs(CRS.from_wkt(open(SRC+'.prj').read()),4326,always_xy=True).transform
F=[]
for sr in r.shapeRecords():
    if not sr.shape.points:continue
    g=make_valid(transform(t,shape(sr.shape.__geo_interface__)))
    F.append((int(sr.record['JENIS_ZONA']),float(sr.record['MEAN'] or 0),float(sr.record['PSTDDEV'] or 0),int(float(sr.record['COUNT_'] or 0)),g))
out=[]
for j in (1,2):
    grp=[f for f in F if f[0]==j]
    simp=list(coverage_simplify([f[4] for f in grp],0.00004))
    for f,g in zip(grp,simp):
        out.append({'type':'Feature','properties':{'j':j,'v':round(f[1]),'r':round(f[2],1),'n':f[3]},'geometry':json.loads(json.dumps(mapping(g),default=float))})
def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0],(list,tuple)) else [round(c[0],5),round(c[1],5)]
for f in out:f['geometry']['coordinates']=rnd(f['geometry']['coordinates'])
# nilai pembanding per zona 2026: rata-rata tertimbang luas irisan dari poligon 2025 dengan jenis sama
g=open('zona_geo.js').read();G=json.loads(g[g.index('{'):g.rindex('}')+1])
d=open('data.js').read();D=json.loads(d[d.index('{'):d.rindex('}')+1]);gn={z['zona']:z['guna'] for z in D['zones']}
orig={j:[(f[4],f[1]) for f in F if f[0]==j] for j in (1,2)}
trees={j:STRtree([a for a,_ in orig[j]]) for j in (1,2)}
cmp={}
for f in G['features']:
    z=f['properties']['z'];j=2 if gn.get(z)=='Pertanian' else 1
    gm=make_valid(shape(f['geometry']));A=gm.area;s=w=0
    for i in trees[j].query(gm):
        a,v=orig[j][i]
        if v<=0:continue
        ia=gm.intersection(a).area
        s+=ia*v;w+=ia
    cmp[z]={'v':round(s/w) if w else None,'c':round(w/A,2) if A else 0}
open('znt25_geo.js','w').write('window.ZNT25='+json.dumps({'fc':{'type':'FeatureCollection','features':out},'cmp':cmp},separators=(',',':'))+';')
print(len(out),'poligon;',sum(1 for v in cmp.values() if v['v']),'zona punya pembanding')
