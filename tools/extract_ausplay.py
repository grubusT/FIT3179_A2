import pandas as pd, sys, warnings
warnings.filterwarnings('ignore')
RAW='raw/'; OUT='data/'  # run from the repo root; raw/ holds the AusPlay workbooks
F25=RAW+'7f8df3ee-C4S-AusPlay-National-Data-Tables-30-April-2026.xlsx'
FILES={'2024 (Jan-Dec)':RAW+'a6442bf8-C4S-AusPlay-National-data-tables-January-to-December-2024.xlsx',
       '2024-25 (Jul-Jun)':RAW+'d03cd9ef-C4S-AusPlay-National-Data-Tables-13-November-2025.xlsx',
       '2025 (Jan-Dec)':F25}
OUTDOOR=['Bush walking','Cycling','Fishing (recreational)','Surfing','Canoeing/Kayaking','Mountain biking',
 'Rock climbing/Abseiling/Caving','Ski & snowboard','Sailing','Equestrian','Paddle sports','Underwater sports',
 'Lifesaving surf','Orienteering','Rogaining','Scouts','Guides']
def find(f,name):
    for s,df in pd.read_excel(f,sheet_name=None,header=None).items():
        if s=='Index': continue
        r=df[df[0].astype(str).str.strip()=='Table name:']
        if len(r) and name in ' '.join(map(str,r.iloc[0].tolist())): return df.reset_index(drop=True)
    raise KeyError(name)
def activity(df,cols):
    df=df.dropna(how='all',axis=1)
    hr=[i for i in range(len(df)) if 'Males' in [str(v).strip() for v in df.iloc[i].tolist()]][0]
    hdr=[str(v).strip() for v in df.iloc[hr].tolist()]
    first=df[df[0].astype(str).str.strip()=='Adventure racing'].index[0]
    block=df.loc[first:first+145]
    block=block[block[0].isin(OUTDOOR)]
    block.columns=[0]+[str(h).replace('#','') for h in hdr[1:]]
    return block.rename(columns={0:'activity'})
# 1+2: 2025 adult & child activity rates by sex/age (long format)
for tbl,fn in [('Participation by activity (adults)','outdoor_activity_adults_2025.csv'),
               ('Participation by activity (children)','outdoor_activity_children_2025.csv')]:
    b=activity(find(F25,tbl),None)
    long=b.melt(id_vars='activity',var_name='group',value_name='rate')
    long['group_type']=long['group'].map(lambda g:'Total' if g=='Total' else ('Sex' if g in('Males','Females') else 'Age'))
    long['rate']=(long['rate'].astype(float)*100).round(2)
    long.to_csv(OUT+fn,index=False); print(fn,len(long))
# 3: trend across 3 releases (adults, total)
rows=[]
for period,f in FILES.items():
    b=activity(find(f,'Participation by activity (adults)'),None)
    for _,r in b.iterrows(): rows.append({'period':period,'activity':r['activity'],'rate':round(float(r['Total'])*100,2)})
pd.DataFrame(rows).to_csv(OUT+'outdoor_activity_trend.csv',index=False); print('trend',len(rows))
# 4: motivations (2025) by sex x age
df=find(F25,'Motivations for participation (adults)').dropna(how='all',axis=1)
mot=[str(m).replace('\n',' ').replace('  ',' ').strip() for m in df.iloc[12].tolist()[2:]]
rows=[];sex=None
for i in range(14,40):
    a,g=df.iloc[i,0],df.iloc[i,1]
    if pd.isna(g): continue
    if str(a) in('All','Males','Females'): sex={'All':'All'}.get(a,a)
    for m,v in zip(mot,df.iloc[i,2:].tolist()):
        if pd.notna(v): rows.append({'sex':sex,'age':str(g).strip(),'motivation':m,'share':round(float(v)*100,1)})
pd.DataFrame(rows).to_csv(OUT+'motivations_2025.csv',index=False); print('motivations',len(rows))
# 5: places where activity took place (2025, adults)
df=find(F25,'Places where activity took place (adults)').dropna(how='all',axis=1)
pl=[str(m).replace('\n',' ').replace('  ',' ').strip() for m in df.iloc[12].tolist()[2:]]
rows=[];sex=None
for i in range(14,40):
    a,g=df.iloc[i,0],df.iloc[i,1]
    if pd.isna(g): continue
    if str(a) in('All','Males','Females'): sex=a
    for m,v in zip(pl,df.iloc[i,2:].tolist()):
        if pd.notna(v) and m!='Total': rows.append({'sex':sex,'age':str(g).strip(),'place':m,'rate':round(float(v)*100,1)})
pd.DataFrame(rows).to_csv(OUT+'places_2025.csv',index=False); print('places',len(rows))
# 6: state participation by frequency (2024, 2025)
df=find(F25,'Frequency of participation by state/territory (adults)').dropna(how='all',axis=1)
states=df.iloc[12].tolist()[3:]
rows=[];sex=year=None
for i in range(14,34):
    if pd.notna(df.iloc[i,0]): sex=df.iloc[i,0]
    if pd.notna(df.iloc[i,1]): year=int(df.iloc[i,1])
    freq=df.iloc[i,2]
    if pd.isna(freq): continue
    for s,v in zip(states,df.iloc[i,3:].tolist()):
        rows.append({'sex':sex,'year':year,'frequency':freq,'state':s,'rate':round(float(v)*100,1)})
pd.DataFrame(rows).to_csv(OUT+'state_participation.csv',index=False); print('state',len(rows))
