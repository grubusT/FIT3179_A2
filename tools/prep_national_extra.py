import pandas as pd, warnings; warnings.filterwarnings('ignore')
F='raw/AusPlay-National-Data-Tables-30-April-2026.xlsx'; OUT='data/'  # run from the repo root
def table(sheet):
    x=pd.read_excel(F,sheet_name=sheet,header=None)
    hr=[i for i in range(30) if 'Males' in [str(v).strip() for v in x.iloc[i].tolist()]][0]
    hdr=[str(v).strip().replace('#','') for v in x.iloc[hr].tolist()]; hdr[0]='activity'
    first=x[x[0].astype(str).str.strip()=='Adventure racing'].index[0]
    last=x[(x[0].astype(str).str.strip()=='Yoga')].index[0]
    b=x.loc[first:last].copy(); b.columns=hdr
    b=b.loc[:,~pd.Series(hdr).isin(['nan']).values]
    return b
b=table('17'); ages=['15-17','18-24','25-34','35-44','45-54','55-64','65+']
for a in ages+['Total']: b[a]=pd.to_numeric(b[a],errors='coerce')
b=b.dropna(subset=ages)
r=b.set_index('activity')[ages].rank(ascending=False,method='first')
keep=r[(r<=7).any(axis=1)].index
print(r.loc[keep].astype(int).to_string())
rows=[]
for act in keep:
    for a in ages: rows.append({'activity':act,'age':a,'rank':int(r.loc[act,a]),'rate':round(b.set_index('activity').loc[act,a]*100,1)})
pd.DataFrame(rows).to_csv(OUT+'activity_rank_by_age_2025.csv',index=False)

# ---- children's barriers (table 14): share of non-participating... check base in header
x=pd.read_excel(F,sheet_name='14',header=None)
print(x.iloc[9:14,0:4].to_string())
hr=[i for i in range(30) if str(x.iloc[i,2]).strip().startswith('Wrong age')][0]
cols=[str(v).replace('\n',' ').replace('  ',' ').strip() for v in x.iloc[hr].tolist()]
rows=[]
for i in range(hr+1,hr+40):
    a,g=str(x.iloc[i,0]).strip(),str(x.iloc[i,1]).strip()
    if 'Estimated' in ' '.join(map(str,x.iloc[i].tolist())): break
    if g=='nan': continue
    for c,v in zip(cols[2:],x.iloc[i,2:].tolist()):
        if pd.notna(v) and c!='nan': rows.append({'group':a if a!='nan' else '', 'sub':g,'barrier':c,'share':round(float(v)*100,1)})
d=pd.DataFrame(rows); print(d[d['sub']=='Total'].sort_values('share',ascending=False).head(25).to_string())
d.to_csv(OUT+'barriers_children_2025.csv',index=False)

# ---- participation gaps (table 1): at least once per week, by group
x=pd.read_excel(F,sheet_name='1',header=None)
rows=[];cat=None
for i in range(15,75):
    c,g=x.iloc[i,0],x.iloc[i,1]
    if pd.notna(c) and str(c).strip() not in('Total',): cat=str(c).strip()
    if pd.isna(g) or cat is None: continue
    yr,wk=x.iloc[i,2],x.iloc[i,10]
    if pd.isna(yr): continue
    rows.append({'category':cat,'group':str(g).strip(),'yearly':round(float(yr)*100,1),'weekly':round(float(wk)*100,1)})
d=pd.DataFrame(rows); print(d.to_string()); d.to_csv(OUT+'participation_gaps_2025.csv',index=False)
