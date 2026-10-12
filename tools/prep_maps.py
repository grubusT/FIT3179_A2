"""Builds the map and state-comparison data from AusPlay state tables and CAPAD 2024.
Run from the repo root with the raw downloads in raw/ (not committed)."""
import pandas as pd, glob, re, warnings; warnings.filterwarnings('ignore')
OUT = 'data/'
ACTS = ['Bush walking', 'Cycling', 'Surfing', 'Fishing (recreational)', 'Canoeing/Kayaking', 'Mountain biking']
STATE_NAMES = {'NSW': 'New South Wales', 'VIC': 'Victoria', 'QLD': 'Queensland', 'SA': 'South Australia',
               'WA': 'Western Australia', 'TAS': 'Tasmania', 'NT': 'Northern Territory', 'ACT': 'Australian Capital Territory'}

def adult_activity_table(path):
    for name, df in pd.read_excel(path, sheet_name=None, header=None).items():
        if name == 'Index': continue
        r = df[df[0].astype(str).str.strip() == 'Table name:']
        if len(r) and 'Participation by activity (adults)' in ' '.join(map(str, r.iloc[0].tolist())):
            return df
    raise KeyError(path)

rows = []
for path in sorted(glob.glob('raw/states/*.xlsx')):
    st = re.search(r'AusPlay-([A-Z]+)-Data', path).group(1)
    df = adult_activity_table(path)
    hits = df[df[0].astype(str).str.strip().isin(ACTS)]
    for act in ACTS:
        h = hits[hits[0].astype(str).str.strip() == act]
        rate_row, num_row = h.iloc[0], h.iloc[1]          # first block = rates, second = estimated participants
        flag = str(rate_row[2]) if pd.notna(rate_row[2]) else ''
        rows.append({'state': st, 'state_name': STATE_NAMES[st], 'activity': act,
                     'rate': round(float(rate_row[1]) * 100, 1), 'participants': round(float(num_row[1])),
                     'reliability': flag})
d = pd.DataFrame(rows)
d.to_csv(OUT + 'state_outdoor_activity_2025.csv', index=False)
print(d.pivot(index='state', columns='activity', values='rate'))
print(d[d.reliability != ''][['state', 'activity', 'reliability']].to_string())

# ---- CAPAD 2024 (terrestrial): exclude OVERLAP=2 records so overlapping areas are not double counted
c = pd.read_csv('raw/capad.csv', low_memory=False)
c = c[c.STATE.isin(STATE_NAMES)]
# State land areas, km2 (Geoscience Australia, "Area of Australia - States and Territories")
LAND = {'NSW': 800642, 'VIC': 227444, 'QLD': 1730648, 'SA': 983482, 'WA': 2527013, 'TAS': 68401, 'NT': 1349129, 'ACT': 2358}
s = (c[c.OVERLAP == 1].groupby('STATE').GIS_AREA.sum() / 100).rename('protected_km2').reset_index()
s['state_name'] = s.STATE.map(STATE_NAMES)
s['land_km2'] = s.STATE.map(LAND)
s['pct_protected'] = (s.protected_km2 / s.land_km2 * 100).round(1)
s['protected_km2'] = s.protected_km2.round(0).astype(int)
s['n_areas'] = s.STATE.map(c.groupby('STATE').size())
s.rename(columns={'STATE': 'state'}).to_csv(OUT + 'state_protected_2024.csv', index=False)
print(s.to_string()); print('national %', round(s.protected_km2.sum() / sum(LAND.values()) * 100, 1))

# ---- protected areas as points, grouped by who manages them
def manager(r):
    if r.TYPE == 'Indigenous Protected Area' or r.GOVERNANCE == 'C': return 'Indigenous Protected Area'
    if r.GOVERNANCE == 'P': return 'Private land'
    if 'National Park' in str(r.TYPE): return 'National park'
    return 'Other public reserve'
c['manager'] = c.apply(manager, axis=1)
p = c[c.GIS_AREA >= 1000][['NAME', 'TYPE', 'STATE', 'manager', 'GIS_AREA', 'LONGITUDE', 'LATITUDE']].copy()  # 10 km2 and larger
p.columns = ['name', 'type', 'state', 'manager', 'area_km2', 'lon', 'lat']
p['area_km2'] = (p.area_km2 / 100).round(1); p['lon'] = p.lon.round(3); p['lat'] = p.lat.round(3)
p.sort_values('area_km2', ascending=False).to_csv(OUT + 'protected_areas_points_2024.csv', index=False)
print(len(p), p.manager.value_counts().to_dict())
print((c.groupby('manager').GIS_AREA.sum() / c.GIS_AREA.sum() * 100).round(1).to_dict())
