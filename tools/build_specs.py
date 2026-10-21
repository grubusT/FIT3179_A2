"""Generates the Vega-Lite specs in specs/ (one readable JSON file per chart).

Run from the repo root:  python3 tools/build_specs.py
Editing the JSON files directly also works; this script just keeps the shared
palette and conventions consistent across charts.
"""
import json, os

SCHEMA = "https://vega.github.io/schema/vega-lite/v5.json"

# Palette (validated for colour-blind separation; see README)
GREEN = "#2e7d4f"   # outdoors / nature
OCHRE = "#d0901f"   # accent, annotations
BLUE = "#2a74a8"    # men
RUST = "#a8462e"    # women; team sports in the bump chart
OLIVE = "#7a8f2a"
GREY = "#c3ccbf"    # context marks
INK = "#1e2b24"
MUTED = "#4b5b51"
NOTE = {"fontSize": 12, "fontStyle": "italic", "color": MUTED}

OUT = "specs/"


# Numeric columns in each CSV. Declaring them stops Vega-Lite treating numbers as text
# inside transforms (e.g. min/max would otherwise compare "9.9" > "14.0").
NUMERIC = {
    "rch_outdoor_play_2022.csv": ["age_order", "share"],
    "activity_rank_by_age_2025.csv": ["rank", "rate"],
    "outdoor_activity_adults_2025.csv": ["rate"],
    "motivations_2025.csv": ["share"],
    "places_2025.csv": ["rate"],
    "vce_oes_enrolments.csv": ["year", "male", "female", "total", "pct_female"],
    "participation_gaps_2025.csv": ["yearly", "weekly"],
    "state_outdoor_activity_2025.csv": ["rate", "participants"],
    "state_protected_2024.csv": ["protected_km2", "land_km2", "pct_protected", "n_areas"],
    "protected_areas_points_2024.csv": ["area_km2", "lon", "lat"],
    "state_points.csv": ["lon", "lat", "label_lon", "label_lat"],
}


def add_parse(node):
    if isinstance(node, dict):
        url = node.get("url")
        if isinstance(url, str) and url.endswith(".csv"):
            cols = NUMERIC[url.split("/")[-1]]
            node["format"] = {"type": "csv", "parse": {c: "number" for c in cols}}
        for v in node.values():
            add_parse(v)
    elif isinstance(node, list):
        for v in node:
            add_parse(v)


def save(name, spec, param_layer=None):
    add_parse(spec)
    """param_layer: path of layer indexes that should own the selection params
    (selection params at the top of a layered spec would be duplicated per layer)."""
    if param_layer is not None:
        target = spec
        for i in param_layer:
            target = target["layer"][i]
        target["params"] = spec.pop("params")
    spec = {"$schema": SCHEMA, **spec}
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write("\n")


def note(text, **pos):
    """A hard-coded annotation: one text mark at fixed data coordinates."""
    return {"mark": {"type": "text", "align": "left", "lineBreak": "\n", **NOTE, **pos.pop("mark", {})},
            "data": {"values": [{"t": text, **pos}]},
            "encoding": {"text": {"field": "t"}}}


# ---------------------------------------------------------------- 1. Waffle
PERSON = ("M-0.3,-0.72 a0.28,0.28 0 1,1 0.56,0 a0.28,0.28 0 1,1 -0.56,0 Z "
          "M-0.55,-0.32 L0.55,-0.32 L0.42,0.35 L0.24,0.35 L0.24,1 L0.04,1 L0.04,0.42 "
          "L-0.04,0.42 L-0.04,1 L-0.24,1 L-0.24,0.35 L-0.42,0.35 Z")
save("waffle_outdoor_play.vg.json", {
    "description": "Isotype waffle: 100 children, 45 of whom play outdoors most days (RCH National Child Health Poll, 2022).",
    "width": "container", "height": 240,
    "data": {"sequence": {"start": 0, "stop": 100, "as": "i"}},
    "params": [{"name": "share", "value": 45}],
    "transform": [
        {"calculate": "floor(datum.i / 5)", "as": "col"},
        {"calculate": "datum.i % 5", "as": "row"},
        {"calculate": "datum.i < share ? 'Plays outdoors most days' : 'Does not'", "as": "group"}
    ],
    "mark": {"type": "point", "shape": PERSON, "filled": True, "size": 1150, "strokeWidth": 0},
    "encoding": {
        "x": {"field": "col", "type": "ordinal", "axis": None},
        "y": {"field": "row", "type": "ordinal", "axis": None},
        "color": {"field": "group", "type": "nominal", "title": None,
                  "scale": {"domain": ["Plays outdoors most days", "Does not"], "range": [GREEN, GREY]},
                  "legend": {"orient": "top", "direction": "horizontal", "symbolType": "square", "labelFontSize": 13}},
        "tooltip": [{"field": "group", "title": "This child"}]
    }
})

# ---------------------------------------------------------------- 2. Screens vs outdoors (slope)
save("screens_vs_outdoors.vg.json", {
    "description": "Share of children doing each kind of play most days, by age group (RCH, 2022).",
    "width": "container", "height": 300,
    "data": {"url": "data/rch_outdoor_play_2022.csv"},
    "transform": [{"filter": "datum.where != 'Outside at home'"}],
    "encoding": {
        "x": {"field": "age_group", "type": "ordinal", "sort": {"field": "age_order"}, "title": None,
              "axis": {"labelAngle": 0, "labelFontSize": 12, "domain": False, "ticks": False}},
        "y": {"field": "share", "type": "quantitative", "title": "% of children, most days",
              "scale": {"domain": [0, 80]}, "axis": {"tickCount": 4}},
        "color": {"field": "where", "type": "nominal", "legend": None,
                  "scale": {"domain": ["Inside on a screen", "Outside away from home", "Outside at home", "Inside without a screen"],
                            "range": [RUST, GREEN, "#8fb59a", GREY]}},
        "detail": {"field": "where"}
    },
    "layer": [
        {"mark": {"type": "line", "strokeWidth": 2.5},
         "encoding": {"strokeWidth": {"condition": {"test": "indexof(['Inside on a screen','Outside away from home'], datum.where) >= 0", "value": 3.5}, "value": 1.5}}},
        {"mark": {"type": "point", "filled": True, "size": 70},
         "encoding": {"tooltip": [{"field": "age_group", "title": "Age"}, {"field": "where", "title": "Activity"},
                                  {"field": "share", "title": "% most days"}]}},
        {"transform": [{"filter": "datum.age_order == 3 && datum.where != 'Inside without a screen'"}],
         "mark": {"type": "text", "align": "left", "dx": 10, "fontSize": 12, "fontWeight": 600},
         "encoding": {"text": {"field": "where"}}},
        {"transform": [{"filter": "datum.age_order == 2 && datum.where == 'Inside without a screen'"}],
         "mark": {"type": "text", "align": "left", "dx": 8, "dy": -10, "fontSize": 12, "fontWeight": 600},
         "encoding": {"text": {"value": "Inside, no screen"}}},
        {"transform": [{"filter": "datum.where == 'Inside on a screen' || datum.where == 'Outside away from home'"}],
         "mark": {"type": "text", "dy": -12, "fontSize": 12, "fontWeight": 700},
         "encoding": {"text": {"field": "share", "format": ".0f"}, "color": {"value": INK}}}
    ],
    "config": {"padding": {"right": 150}}
})

# ---------------------------------------------------------------- 7. Bump chart
OUTDOOR = ["Bush walking", "Cycling", "Golf"]
TEAM = ["Basketball", "Football/soccer"]
save("activity_rank_bump.vg.json", {
    "description": "Bump chart: rank of each activity by number of participants, across adult age groups (AusPlay 2025). Lines leaving the bottom fall out of the top 12.",
    "width": "container", "height": 380,
    "data": {"url": "data/activity_rank_by_age_2025.csv"},
    "params": [{"name": "focus", "select": {"type": "point", "fields": ["activity"], "on": "pointerover", "clear": "pointerout"}}],
    "encoding": {
        "x": {"field": "age", "type": "ordinal", "title": "Age group",
              "sort": ["15-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
              "axis": {"labelAngle": 0, "domain": False, "ticks": False, "grid": False}},
        "y": {"field": "rank", "type": "quantitative", "title": "Rank",
              "scale": {"domain": [12.5, 0.5], "reverse": False, "nice": False},
              "axis": {"values": [1, 3, 5, 7, 9, 11], "grid": False}},
        "color": {"field": "group", "type": "nominal", "legend": None,
                  "scale": {"domain": ["Bush walking", "Cycling", "Golf", "Team sport", "Other"],
                            "range": [GREEN, OLIVE, OCHRE, RUST, GREY]}},
        "detail": {"field": "activity"},
        "opacity": {"condition": [{"param": "focus", "empty": True, "value": 1}], "value": 0.25}
    },
    "transform": [
        {"calculate": f"indexof({json.dumps(OUTDOOR)}, datum.activity) >= 0 ? datum.activity : indexof({json.dumps(TEAM)}, datum.activity) >= 0 ? 'Team sport' : 'Other'", "as": "group"},
        {"calculate": "datum.activity == 'Bush walking' ? 'Bushwalking' : datum.activity == 'Walking (Recreational)' ? 'Walking' : datum.activity", "as": "label"}
    ],
    "layer": [
        {"mark": {"type": "line", "clip": True, "interpolate": "monotone"},
         "encoding": {"strokeWidth": {"condition": {"test": "datum.group != 'Other'", "value": 3.5}, "value": 2}}},
        {"mark": {"type": "point", "filled": True, "size": 90, "clip": True, "stroke": "#eef1ea", "strokeWidth": 1.5},
         "encoding": {"tooltip": [{"field": "label", "title": "Activity"}, {"field": "age", "title": "Age"},
                                  {"field": "rank", "title": "Rank"}, {"field": "rate", "title": "% of age group taking part"}]}},
        {"transform": [{"filter": "datum.age == '65+' && datum.rank <= 12"}],
         "mark": {"type": "text", "align": "left", "dx": 10, "fontSize": 12, "fontWeight": 600},
         "encoding": {"text": {"field": "label"}}},
        {"transform": [{"filter": "datum.age == '15-17' && datum.rank <= 12 && datum.group == 'Team sport'"}],
         "mark": {"type": "text", "align": "left", "dx": 9, "dy": -11, "fontSize": 12, "fontWeight": 600},
         "encoding": {"text": {"field": "label"}}},
        {"data": {"values": [{"age": "35-44", "rank": 3}]},
         "mark": {"type": "text", "align": "left", "dx": 6, "dy": -26, "lineBreak": "\n", **NOTE},
         "encoding": {"text": {"value": "Bushwalking reaches 3rd\nfrom age 35"}, "color": {"value": MUTED},
                      "opacity": {"value": 1}}},
        {"data": {"values": [{"age": "55-64", "rank": 12.3}]},
         "mark": {"type": "text", "align": "center", "dy": -6, **NOTE},
         "encoding": {"text": {"value": "Team sports drop out of the top 12"}, "color": {"value": MUTED},
                      "opacity": {"value": 1}}}
    ],
    "config": {"padding": {"right": 110}}
}, param_layer=[1])

# ---------------------------------------------------------------- 8. Heatmap
ACTS = ["Bush walking", "Cycling", "Surfing", "Fishing (recreational)", "Canoeing/Kayaking",
        "Underwater sports", "Ski & snowboard", "Mountain biking", "Rock climbing/Abseiling/Caving", "Sailing"]
save("activity_age_heatmap.vg.json", {
    "description": "Heatmap of outdoor activity participation by age group, Australian adults 2025 (AusPlay).",
    "width": "container", "height": 330,
    "data": {"url": "data/outdoor_activity_adults_2025.csv"},
    "transform": [
        {"filter": "datum.group_type === 'Age'"},
        {"filter": {"field": "activity", "oneOf": ACTS}},
        {"calculate": "replace(replace(replace(datum.activity, 'Bush walking', 'Bushwalking'), 'Rock climbing/Abseiling/Caving', 'Climbing & caving'), 'Fishing (recreational)', 'Fishing')", "as": "label"}
    ],
    "encoding": {
        "x": {"field": "group", "type": "ordinal", "title": "Age group", "axis": {"labelAngle": 0, "orient": "top", "domain": False, "ticks": False}},
        "y": {"field": "label", "type": "nominal", "title": None, "sort": {"field": "rate", "op": "mean", "order": "descending"},
              "axis": {"domain": False, "ticks": False, "labelFontSize": 12.5}}
    },
    "layer": [
        {"mark": {"type": "rect", "cornerRadius": 3, "stroke": "#eef1ea", "strokeWidth": 2},
         "encoding": {
             "color": {"field": "rate", "type": "quantitative", "title": "% taking part",
                       "scale": {"type": "pow", "exponent": 0.5, "range": ["#e7efe3", "#a9c8a6", "#4f8f5c", "#1f5a36"]},
                       "legend": {"orient": "bottom", "direction": "horizontal", "gradientLength": 220, "values": [1, 5, 10, 20]}},
             "tooltip": [{"field": "label", "title": "Activity"}, {"field": "group", "title": "Age"},
                         {"field": "rate", "title": "% of age group", "format": ".1f"}]}},
        {"mark": {"type": "text", "fontSize": 11.5},
         "encoding": {"text": {"field": "rate", "type": "quantitative", "format": ".1f"},
                      "color": {"condition": {"test": "datum.rate > 6", "value": "white"}, "value": INK}}}
    ]
})

# ---------------------------------------------------------------- 9. Gender dumbbell
# Two panels, both starting at 0%: the two big activities, then the smaller ones on a
# shorter scale so their gaps stay visible without a log scale.
G_ACTS = ["Bush walking", "Cycling", "Surfing", "Fishing (recreational)", "Canoeing/Kayaking",
          "Mountain biking", "Ski & snowboard", "Equestrian", "Rock climbing/Abseiling/Caving", "Sailing"]
G_PREP = [
    {"filter": {"field": "group", "oneOf": ["Males", "Females"]}},
    {"filter": {"field": "activity", "oneOf": G_ACTS}},
    {"calculate": "datum.group == 'Females' ? 'Women' : 'Men'", "as": "sex"},
    # Equestrian is labelled "Horse riding" for a general audience
    {"calculate": "replace(replace(replace(replace(datum.activity, 'Bush walking', 'Bushwalking'), 'Rock climbing/Abseiling/Caving', 'Climbing & caving'), 'Fishing (recreational)', 'Fishing'), 'Equestrian', 'Horse riding')", "as": "label"},
    {"joinaggregate": [{"op": "max", "field": "rate", "as": "top"}], "groupby": ["activity"]},
]


def dumbbell_panel(title, test, xmax, ticks, notes):
    return {
        "title": {"text": title, "fontSize": 13, "font": "Figtree, sans-serif", "fontWeight": 700, "color": INK, "offset": 8},
        "width": 380, "height": {"step": 30},
        "transform": [{"filter": test}],
        "encoding": {
            "y": {"field": "label", "type": "nominal", "title": None, "sort": {"field": "top", "op": "max", "order": "descending"},
                  "axis": {"domain": False, "ticks": False, "labelFontSize": 12.5, "grid": True, "gridDash": [2, 3], "minExtent": 120}},
            "x": {"field": "rate", "type": "quantitative", "title": "% of adults taking part",
                  "scale": {"domain": [0, xmax]}, "axis": {"values": ticks}}
        },
        "layer": [
            {"mark": {"type": "line", "color": "#9aa79a", "strokeWidth": 2.5}, "encoding": {"detail": {"field": "label"}}},
            {"mark": {"type": "point", "filled": True, "size": 110, "opacity": 1, "stroke": "#eef1ea", "strokeWidth": 1.5},
             "encoding": {
                 "color": {"field": "sex", "type": "nominal", "title": None, "scale": {"domain": ["Women", "Men"], "range": [RUST, BLUE]},
                           "legend": {"orient": "top", "direction": "horizontal", "symbolSize": 120, "labelFontSize": 13}},
                 "shape": {"field": "sex", "scale": {"domain": ["Women", "Men"], "range": ["circle", "diamond"]}, "legend": None},
                 "tooltip": [{"field": "label", "title": "Activity"}, {"field": "sex", "title": "Group"},
                             {"field": "rate", "title": "% taking part", "format": ".2f"}]}},
            *notes
        ]
    }


save("gender_dumbbell.vg.json", {
    "description": "Dumbbell chart comparing women's and men's participation in outdoor activities, 2025 (AusPlay). Two panels, both starting at 0%.",
    "data": {"url": "data/outdoor_activity_adults_2025.csv"},
    "transform": G_PREP,
    "vconcat": [
        dumbbell_panel("The two biggest activities", "datum.top >= 5", 20, [0, 5, 10, 15, 20],
                       [note("Women lead", rate=18.6, label="Bushwalking", mark={"align": "right", "dx": -12, "dy": -12})]),
        dumbbell_panel("Smaller activities (shorter scale)", "datum.top < 5", 2, [0, 0.5, 1, 1.5, 2],
                       [note("Men about four\ntimes as likely", rate=1.25, label="Mountain biking", mark={"dx": 10, "dy": 2}),
                        note("Women about five\ntimes as likely", rate=0.8, label="Horse riding", mark={"dx": 10, "dy": 2})])
    ],
    "spacing": 28,
    "resolve": {"scale": {"color": "shared", "shape": "shared"}, "legend": {"color": "shared"}}
})

# ---------------------------------------------------------------- 10. Reasons for being active (simple ranked bars)
LABELS = ("{'Physical health or fitness':'Fitness','Fun/enjoyment':'Fun','To lose weight/ keep weight off/tone':'Weight',"
          "'To be outdoors/to enjoy nature':'Being outdoors','Social reasons':'Social','Psychological/ mental health/ therapy':'Mental health',"
          "'Sense of achievement':'Achievement','Hobby':'Hobby','Walk the dog':'Walk the dog','Training purposes':'Training',"
          "'Learn a new skill':'Learn a new skill','Performance or competition':'Competition','Way of getting around':'Getting around',"
          "'Physio/rehab/ physical therapy/post-op':'Rehab','To be a good role model':'Role model','Professional/ part of my job':'For work'}")
save("motivations_bar.vg.json", {
    "description": "Ranked bar chart of the top 10 reasons Australians give for being active, with an age-group menu (AusPlay 2025).",
    "width": "container", "height": {"step": 30},
    "data": {"url": "data/motivations_2025.csv"},
    "params": [{"name": "Age", "value": "Total",
                "bind": {"input": "select", "options": ["Total", "15-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
                         "labels": ["All adults", "15 to 17", "18 to 24", "25 to 34", "35 to 44", "45 to 54", "55 to 64", "65 and over"],
                         "name": "Show age group  "}}],
    "transform": [
        {"filter": "datum.sex == 'All' && datum.age == Age"},
        {"window": [{"op": "row_number", "as": "r"}], "sort": [{"field": "share", "order": "descending"}]},
        {"filter": "datum.r <= 10"},
        {"calculate": LABELS + "[datum.motivation]", "as": "label"},
        {"calculate": "datum.label == 'Being outdoors'", "as": "nature"}
    ],
    "encoding": {
        "y": {"field": "label", "type": "nominal", "title": None, "sort": {"field": "share", "op": "max", "order": "descending"},
              "axis": {"domain": False, "ticks": False, "labelFontSize": 13, "labelPadding": 8,
                       "labelColor": {"condition": {"test": "datum.value == 'Being outdoors'", "value": GREEN}, "value": INK},
                       "labelFontWeight": {"condition": {"test": "datum.value == 'Being outdoors'", "value": 700}, "value": 400}}},
        "x": {"field": "share", "type": "quantitative", "title": "% of active adults", "scale": {"domain": [0, 80]},
              "axis": {"values": [0, 20, 40, 60, 80], "grid": True}}
    },
    "layer": [
        {"mark": {"type": "bar", "cornerRadiusEnd": 3, "height": {"band": 0.72}},
         "encoding": {"color": {"field": "nature", "type": "nominal", "legend": None, "scale": {"domain": [True, False], "range": [GREEN, "#b7c6b4"]}},
                      "tooltip": [{"field": "motivation", "title": "Reason"}, {"field": "share", "title": "% of active adults"}]}},
        {"mark": {"type": "text", "align": "left", "dx": 5, "fontSize": 12.5, "fontWeight": 700, "color": INK},
         "encoding": {"text": {"field": "share", "format": ".0f"}}}
    ]
})

# ---------------------------------------------------------------- 11. Places small multiples
PLACES = ["Public space", "Home environment", "Gym/fitness club/sports/ leisure centre",
          "Free community facilities", "Sports club or association facilities", "Educational institution facilities"]
save("places_small_multiples.vg.json", {
    "description": "Small multiples: where Australian adults are active, by age group (AusPlay 2025).",
    "data": {"url": "data/places_2025.csv"},
    "transform": [
        {"filter": "datum.sex == 'All' && datum.age != 'Total'"},
        {"filter": {"field": "place", "oneOf": PLACES}},
        {"calculate": "{'Public space':'Parks, trails and beaches','Home environment':'At home','Gym/fitness club/sports/ leisure centre':'Gyms and leisure centres','Free community facilities':'Free community facilities','Sports club or association facilities':'Sports clubs','Educational institution facilities':'School and uni facilities'}[datum.place]", "as": "label"},
        {"calculate": "datum.place == 'Public space' ? 'park' : datum.place == 'Educational institution facilities' ? 'school' : 'other'", "as": "hl"}
    ],
    "facet": {"field": "label", "type": "nominal", "title": None,
              "sort": ["Parks, trails and beaches", "School and uni facilities", "Gyms and leisure centres", "At home", "Free community facilities", "Sports clubs"],
              "header": {"labelFontSize": 14, "labelFontWeight": 600, "labelColor": INK, "labelAnchor": "start", "labelPadding": 6}},
    "columns": 3,
    "spec": {
        "width": 300, "height": 130,
        "layer": [
            {"mark": {"type": "bar", "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3, "width": {"band": 0.72}},
             "encoding": {
                 "x": {"field": "age", "type": "ordinal", "title": None, "axis": {"labelAngle": 0, "labelFontSize": 10.5, "domain": False, "ticks": False}},
                 "y": {"field": "rate", "type": "quantitative", "title": None, "scale": {"domain": [0, 80]}, "axis": {"values": [0, 25, 50, 75], "labelFontSize": 10}},
                 "color": {"field": "hl", "legend": None, "scale": {"domain": ["park", "school", "other"], "range": [GREEN, OCHRE, "#b7c6b4"]}},
                 "tooltip": [{"field": "label", "title": "Place"}, {"field": "age", "title": "Age"}, {"field": "rate", "title": "% active here"}]}},
            {"transform": [{"filter": "datum.hl != 'other' && (datum.age == '15-17' || datum.age == '65+')"}],
             "mark": {"type": "text", "dy": -8, "fontSize": 11, "fontWeight": 700, "color": INK},
             "encoding": {"x": {"field": "age", "type": "ordinal"}, "y": {"field": "rate", "type": "quantitative"},
                          "text": {"field": "rate", "format": ".0f"}}}
        ]
    },
    "resolve": {"axis": {"x": "independent"}},
    "spacing": {"row": 28, "column": 30}
})

# ---------------------------------------------------------------- 12. VCE line
save("vce_enrolments_line.vg.json", {
    "description": "Annotated line chart of VCE Outdoor and Environmental Studies enrolments, 2014 to 2025 (VCAA). No data published for 2015 and 2016.",
    "width": "container", "height": 320,
    "data": {"url": "data/vce_oes_enrolments.csv"},
    "transform": [{"calculate": "datum.unit == 'Unit 1' ? 'Year 11' : 'Year 12'", "as": "level"}],
    "params": [{"name": "pick", "select": {"type": "point", "fields": ["level"]}, "bind": "legend"}],
    "encoding": {
        "x": {"field": "year", "type": "quantitative", "title": None, "scale": {"domain": [2014, 2025.6]},
              "axis": {"format": "d", "values": [2014, 2016, 2018, 2020, 2022, 2024], "grid": False}},
        "y": {"field": "total", "type": "quantitative", "title": "Students enrolled", "scale": {"domain": [0, 4200]},
              "axis": {"tickCount": 5, "format": ",.0f"}},
    },
    "layer": [
        {"data": {"values": [{"x": 2015.5, "y": 400}]},
         "mark": {"type": "text", "fontSize": 11, "color": MUTED, "fontStyle": "italic"},
         "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"},
                      "text": {"value": "2015 and 2016: no data"}}},
        {"mark": {"type": "line", "strokeWidth": 3, "point": {"filled": True, "size": 60}}, "encoding": {
            "color": {"field": "level", "type": "nominal", "title": "Click to focus",
                      "scale": {"domain": ["Year 11", "Year 12"], "range": [OLIVE, GREEN]},
                      "legend": {"orient": "top-left", "direction": "horizontal", "symbolStrokeWidth": 3}},
            "opacity": {"condition": {"param": "pick", "value": 1}, "value": 0.2},
            "tooltip": [{"field": "year", "title": "Year"}, {"field": "level", "title": "Level"},
                        {"field": "total", "title": "Students", "format": ","}, {"field": "pct_female", "title": "% girls"}]}},
        {"transform": [{"filter": "datum.year == 2025"}],
         "mark": {"type": "text", "align": "left", "dx": 8, "fontSize": 12, "fontWeight": 700},
         "encoding": {"text": {"field": "level"}, "color": {"field": "level", "type": "nominal", "legend": None}}},
        {"data": {"values": [{"year": 2021, "total": 2656}]},
         "mark": {"type": "text", "dy": 22, **NOTE},
         "encoding": {"x": {"field": "year", "type": "quantitative"}, "y": {"field": "total", "type": "quantitative"},
                      "text": {"value": "2021: COVID lockdowns"}}},
        {"data": {"values": [{"year": 2014, "total": 2825}]},
         "mark": {"type": "text", "align": "left", "dx": 6, "dy": 18, **NOTE},
         "encoding": {"x": {"field": "year", "type": "quantitative"}, "y": {"field": "total", "type": "quantitative"},
                      "text": {"value": "2,825 in 2014"}}}
    ],
    "config": {"padding": {"right": 64}}
}, param_layer=[2])

# ---------------------------------------------------------------- 13. VCE gender (diverging)
save("vce_gender_diverging.vg.json", {
    "description": "Diverging bar chart of boys and girls enrolled in VCE Outdoor and Environmental Studies, Year 11 and Year 12 (VCAA).",
    "data": {"url": "data/vce_oes_enrolments.csv"},
    "transform": [
        {"calculate": "datum.unit == 'Unit 1' ? 'Year 11' : 'Year 12'", "as": "level"},
        {"fold": ["male", "female"], "as": ["sex", "n"]},
        {"calculate": "datum.sex == 'male' ? -datum.n : datum.n", "as": "signed"},
        {"calculate": "datum.sex == 'male' ? 'Boys' : 'Girls'", "as": "who"}
    ],
    "facet": {"column": {"field": "level", "type": "nominal", "title": None,
                         "header": {"labelFontSize": 14, "labelFontWeight": 600, "labelColor": INK}}},
    "spec": {
        "width": 230, "height": 260,
        "layer": [
            {"mark": {"type": "bar", "cornerRadiusEnd": 3, "height": {"band": 0.75}},
             "encoding": {
                 "y": {"field": "year", "type": "ordinal", "title": None, "sort": "descending", "axis": {"domain": False, "ticks": False}},
                 "x": {"field": "signed", "type": "quantitative", "title": "← Boys    Girls →", "scale": {"domain": [-2300, 2300]},
                       "axis": {"labelExpr": "format(abs(datum.value), ',')", "values": [-2000, -1000, 0, 1000, 2000]}},
                 "color": {"field": "who", "type": "nominal", "title": None, "scale": {"domain": ["Girls", "Boys"], "range": [RUST, BLUE]},
                           "legend": {"orient": "top", "direction": "horizontal"}},
                 "tooltip": [{"field": "year", "title": "Year"}, {"field": "level", "title": "Level"}, {"field": "who", "title": "Group"},
                             {"field": "n", "title": "Students", "format": ","}, {"field": "pct_female", "title": "% girls"}]}},
            {"transform": [{"filter": "datum.sex == 'female'"}],
             "mark": {"type": "text", "align": "left", "dx": 5, "fontSize": 10.5, "color": MUTED},
             "encoding": {"y": {"field": "year", "type": "ordinal", "sort": "descending"},
                          "x": {"field": "signed", "type": "quantitative"},
                          "text": {"field": "pct_female", "type": "quantitative", "format": ".0f"}}}
        ]
    },
    "resolve": {"scale": {"y": "shared"}}
})

# ---------------------------------------------------------------- 14. Who misses out
save("participation_gaps.vg.json", {
    "description": "Small multiples: share of adults active at least once a week, by income, education, disability and Indigenous status (AusPlay 2025).",
    "data": {"url": "data/participation_gaps_2025.csv"},
    "transform": [
        {"filter": {"field": "category", "oneOf": ["Annual household income~^", "Highest education completed",
                                                   "Disability or physical condition that restricts life in some way^",
                                                   "Aboriginal or Torres Strait Islander origin^"]}},
        {"filter": "indexof(['Not stated','Other','Still at secondary school','Refused / don\\'t know'], datum.group) < 0"},
        {"calculate": "{'Annual household income~^':'Household income','Highest education completed':'Highest education','Disability or physical condition that restricts life in some way^':'Disability','Aboriginal or Torres Strait Islander origin^':'First Nations'}[datum.category]", "as": "panel"},
        {"calculate": "{'University degree or higher (including postgraduate diploma)':'University degree','Undergraduate diploma or associate diploma':'Diploma','Certificate, trade qualification or apprenticeship':'Trade or certificate','Highest level of secondary school':'Finished Year 12','Did not complete highest level of school':'Left school early','Yes':'Yes','No':'No'}[datum.group] || datum.group", "as": "label"},
        {"joinaggregate": [{"op": "min", "field": "weekly", "as": "lo"}, {"op": "max", "field": "weekly", "as": "hi"}], "groupby": ["panel"]},
        {"calculate": "datum.weekly == datum.lo ? 'low' : datum.weekly == datum.hi ? 'high' : 'mid'", "as": "tone"},
        {"calculate": "datum.tone == 'low' ? format(datum.weekly, '.0f') + '%, ' + format(datum.hi - datum.lo, '.0f') + ' points behind' : format(datum.weekly, '.0f') + '%'", "as": "vlabel"}
    ],
    "facet": {"field": "panel", "type": "nominal", "title": None, "sort": ["Household income", "Highest education", "Disability", "First Nations"],
              "header": {"labelFontSize": 15, "labelFontWeight": 700, "labelColor": INK, "labelAnchor": "start", "labelPadding": 8}},
    "columns": 2,
    "spec": {
        "width": 370, "height": {"step": 36},
        "encoding": {
            "y": {"field": "label", "type": "nominal", "title": None, "sort": None,
                  "axis": {"domain": False, "ticks": False, "labelFontSize": 13, "minExtent": 150, "maxExtent": 150}},
            "x": {"field": "weekly", "type": "quantitative", "title": "% active at least once a week", "scale": {"domain": [0, 100]},
                  "axis": {"values": [0, 25, 50, 75, 100], "grid": True}}
        },
        "layer": [
            {"mark": {"type": "bar", "cornerRadiusEnd": 3, "height": {"band": 0.7}},
             "encoding": {"color": {"field": "tone", "legend": None, "scale": {"domain": ["low", "mid", "high"], "range": [RUST, "#b7c6b4", GREEN]}},
                          "tooltip": [{"field": "panel", "title": "Grouped by"}, {"field": "label", "title": "Group"},
                                      {"field": "weekly", "title": "% active weekly"}]}},
            {"mark": {"type": "text", "align": "left", "dx": 6, "fontSize": 13, "fontWeight": 700},
             "encoding": {"text": {"field": "vlabel"},
                          "color": {"condition": {"test": "datum.tone == 'low'", "value": RUST}, "value": INK}}}
        ]
    },
    "resolve": {"scale": {"y": "independent"}},
    "spacing": {"row": 40, "column": 60}
})

# ================================================================ MAPS
def note_geo(text, lon, lat, align="left"):
    """An annotation placed at a longitude/latitude."""
    return {"data": {"values": [{"lon": lon, "lat": lat, "t": text}]},
            "mark": {"type": "text", "align": align, "lineBreak": "\n", **NOTE},
            "encoding": {"longitude": {"field": "lon", "type": "quantitative"},
                         "latitude": {"field": "lat", "type": "quantitative"}, "text": {"field": "t"}}}

PROJ = {"type": "conicEqualArea", "parallels": [-18, -36], "rotate": [-134, 0]}
STATES = {"url": "data/aus_states.topojson", "format": {"type": "topojson", "feature": "states"}}
BASE = {"data": STATES, "mark": {"type": "geoshape", "fill": "#dfe6da", "stroke": "#eef1ea", "strokeWidth": 1.5}}

# ---------------------------------------------------------------- 3. Choropleth: % of land protected
save("protected_choropleth.vg.json", {
    "description": "Choropleth map: share of each state's land in protected areas, 30 June 2024 (CAPAD 2024; overlapping areas counted once).",
    "width": "container", "height": 430, "projection": PROJ,
    "layer": [
        {"data": STATES,
         "transform": [{"lookup": "properties.state", "from": {"data": {"url": "data/state_protected_2024.csv"}, "key": "state",
                                                               "fields": ["state_name", "pct_protected", "protected_km2", "n_areas"]}}],
         "mark": {"type": "geoshape", "stroke": "#eef1ea", "strokeWidth": 1.5},
         "encoding": {
             "color": {"field": "pct_protected", "type": "quantitative", "title": "% of land protected",
                       "scale": {"domain": [0, 60], "range": ["#e7efe3", "#1f5a36"]},
                       "legend": {"orient": "bottom-left", "direction": "horizontal", "gradientLength": 180, "values": [0, 20, 40, 60]}},
             "tooltip": [{"field": "state_name", "title": "State"}, {"field": "pct_protected", "title": "% of land protected"},
                         {"field": "protected_km2", "title": "Protected area (km²)", "format": ","},
                         {"field": "n_areas", "title": "Number of protected areas", "format": ","}]}},
        {"data": {"url": "data/state_points.csv"},
         "transform": [{"lookup": "state", "from": {"data": {"url": "data/state_protected_2024.csv"}, "key": "state", "fields": ["pct_protected"]}},
                       {"calculate": "datum.state + '  ' + format(datum.pct_protected, '.0f') + '%'", "as": "lab"}],
         "mark": {"type": "text", "fontSize": 13, "fontWeight": 700},
         "encoding": {"longitude": {"field": "label_lon", "type": "quantitative"}, "latitude": {"field": "label_lat", "type": "quantitative"},
                      "text": {"field": "lab"},
                      "color": {"condition": {"test": "datum.pct_protected > 25 && datum.state != 'ACT' && datum.state != 'TAS'", "value": "white"}, "value": INK}}},
        {"data": {"values": [{"lon": 147.0, "lat": -46.3, "t": "Tasmania protects more than\ntwo-fifths of its land"},
                             {"lon": 151.2, "lat": -19.5, "t": "QLD and NSW\nprotect under 10%"}]},
         "mark": {"type": "text", "align": "left", "lineBreak": "\n", **NOTE},
         "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                      "text": {"field": "t"}}}
    ]
})

# ---------------------------------------------------------------- 4. Dot map: protected areas by manager
# Every dot is the same size, so position and colour carry the meaning. Size is kept
# for the proportional symbol map (chart 5), so the two map idioms stay distinct.
MANAGERS = ["Indigenous Protected Area", "National park", "Other public reserve", "Private land"]
save("parks_point_map.vg.json", {
    "description": "Dot map: every protected area of 10 km² or more, placed at its centre and coloured by who manages it (CAPAD 2024).",
    "width": "container", "height": 500, "projection": PROJ,
    "params": [{"name": "who", "select": {"type": "point", "fields": ["manager"]}, "bind": "legend"}],
    "layer": [
        {"data": STATES, "mark": {"type": "geoshape", "fill": "#dfe6da", "stroke": "#eef1ea", "strokeWidth": 1.5}},
        {"data": {"url": "data/protected_areas_points_2024.csv"},
         "transform": [{"calculate": "indexof(" + json.dumps(MANAGERS[::-1]) + ", datum.manager)", "as": "draw_order"}],
         "mark": {"type": "circle", "size": 34, "stroke": "#ffffff", "strokeWidth": 0.5},
         "encoding": {
             "longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
             "color": {"field": "manager", "type": "nominal", "title": "Managed by (click to filter)",
                       "scale": {"domain": MANAGERS, "range": [OCHRE, GREEN, OLIVE, BLUE]},
                       "legend": {"symbolSize": 120, "labelFontSize": 12.5}},
             "opacity": {"condition": {"param": "who", "value": 0.9}, "value": 0.05},
             "order": {"field": "draw_order"},
             "tooltip": [{"field": "name", "title": "Name"}, {"field": "type", "title": "Type"}, {"field": "manager", "title": "Managed by"},
                         {"field": "state", "title": "State"}, {"field": "area_km2", "title": "Area (km²)", "format": ",.0f"}]}},
        note_geo("The 92 orange dots are Indigenous Protected Areas.\nFew in number, they cover half of all protected land.", 117.5, -38.2, "center"),
        note_geo("Hundreds of smaller reserves\ncrowd the south-east", 156.0, -38.5, "left")
    ],
    "config": {"legend": {"orient": "right", "symbolType": "circle"}}
}, param_layer=[1])

# ---------------------------------------------------------------- 5. Proportional symbol map: bushwalkers
save("bushwalking_symbol_map.vg.json", {
    "description": "Proportional symbol map: number of adult bushwalkers in each state (circle size) and share of adults who bushwalk (colour), 2025 (AusPlay state tables). Click a state to highlight it in the next chart.",
    "width": "container", "height": 430, "projection": PROJ,
    "params": [{"name": "pickState", "select": {"type": "point", "fields": ["state"], "on": "click"}, "value": [{"state": "TAS"}]}],
    "layer": [
        {"data": STATES, "mark": {"type": "geoshape", "fill": "#dfe6da", "stroke": "#eef1ea", "strokeWidth": 1.5}},
        {"data": {"url": "data/state_outdoor_activity_2025.csv"},
         "transform": [{"filter": "datum.activity == 'Bush walking'"},
                       {"lookup": "state", "from": {"data": {"url": "data/state_points.csv"}, "key": "state",
                                                    "fields": ["lon", "lat", "label_lon", "label_lat"]}}],
         "layer": [
             {"mark": {"type": "circle", "stroke": "white", "strokeWidth": 1.5, "opacity": 0.92, "cursor": "pointer"},
              "encoding": {
                  "longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                  "size": {"field": "participants", "type": "quantitative", "title": "Adult bushwalkers",
                           "scale": {"type": "sqrt", "range": [60, 5200], "domain": [0, 1300000]},
                           "legend": {"values": [100000, 500000, 1000000], "format": ".2s", "symbolFillColor": "#9aa79a", "symbolStrokeWidth": 0}},
                  "color": {"field": "rate", "type": "quantitative", "title": "% of adults who bushwalk",
                            "scale": {"domain": [14, 28], "range": ["#a9c8a6", "#1f5a36"]},
                            "legend": {"values": [15, 20, 25], "gradientLength": 120}},
                  "strokeWidth": {"condition": {"param": "pickState", "empty": False, "value": 4}, "value": 1.5},
                  "stroke": {"condition": {"param": "pickState", "empty": False, "value": OCHRE}, "value": "white"},
                  "tooltip": [{"field": "state_name", "title": "State"}, {"field": "participants", "title": "Adult bushwalkers", "format": ","},
                              {"field": "rate", "title": "% of adults"}]}},
             {"transform": [{"calculate": "[datum.state, format(datum.rate, '.0f') + '%']", "as": "lab"}],
              "mark": {"type": "text", "fontSize": 12, "fontWeight": 700, "lineHeight": 14, "dy": -6},
              "encoding": {"longitude": {"field": "label_lon", "type": "quantitative"}, "latitude": {"field": "label_lat", "type": "quantitative"},
                           "text": {"field": "lab"},
                           "color": {"condition": {"test": "datum.state == 'ACT' || datum.state == 'TAS' || datum.state == 'NT'", "value": INK}, "value": "white"}}}
         ]},
        {"data": {"values": [{"lon": 149.5, "lat": -45.6, "t": "Tasmanians (28%) and Canberrans (27%)\nare the most likely to bushwalk"}]},
         "mark": {"type": "text", "align": "left", "lineBreak": "\n", **NOTE},
         "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                      "text": {"field": "t"}}}
    ],
    "config": {"legend": {"orient": "right"}}
}, param_layer=[1, 0])

# ---------------------------------------------------------------- 6. Parallel coordinates: state outdoor profiles
# Every axis runs from 0% at the bottom to the highest state at the top, so a line's
# height on an axis shows how close that state is to the leader. Lines are drawn in
# axis order (left to right) using an explicit order channel.
PC_AXES = ["Bushwalking", "Cycling", "Mountain biking", "Canoe & kayak", "Surfing", "Fishing"]
PC_ACTS = ["Bush walking", "Cycling", "Mountain biking", "Canoeing/Kayaking", "Surfing", "Fishing (recreational)"]
PC_BASE = {
    "y": {"field": "norm", "type": "quantitative", "axis": None, "scale": {"domain": [0, 1]}},
}
save("state_parallel_coordinates.vg.json", {
    "description": "Parallel coordinates: each line is a state, each upright axis an outdoor activity. Every axis starts at 0% and tops out at the leading state (AusPlay 2025).",
    "width": "container", "height": 340,
    "data": {"url": "data/state_outdoor_activity_2025.csv"},
    "params": [{"name": "hl", "value": "TAS",
                "bind": {"input": "select", "options": ["TAS", "ACT", "NSW", "VIC", "QLD", "SA", "WA", "NT"],
                         "labels": ["Tasmania", "ACT", "New South Wales", "Victoria", "Queensland", "South Australia", "Western Australia", "Northern Territory"],
                         "name": "Highlight a state  "}}],
    "transform": [
        {"filter": {"field": "activity", "oneOf": PC_ACTS}},
        {"calculate": "replace(replace(replace(datum.activity, 'Bush walking', 'Bushwalking'), 'Fishing (recreational)', 'Fishing'), 'Canoeing/Kayaking', 'Canoe & kayak')", "as": "axis"},
        {"calculate": "indexof(" + json.dumps(PC_AXES) + ", datum.axis)", "as": "axis_i"},
        {"joinaggregate": [{"op": "max", "field": "rate", "as": "hi"}], "groupby": ["activity"]},
        {"calculate": "datum.rate / datum.hi", "as": "norm"},
        {"calculate": "datum.state == hl", "as": "on"}
    ],
    "encoding": {"x": {"field": "axis", "type": "nominal", "title": None, "sort": PC_AXES, "scale": {"padding": 0.25},
        "axis": {"orient": "top", "domain": False, "ticks": False, "labelAngle": 0, "labelPadding": 26, "labelFontSize": 13.5,
                 "labelFontWeight": 600, "labelColor": INK, "grid": True, "gridColor": "#9aa79a", "gridWidth": 1.5}}},
    "layer": [
        # every state, drawn quietly
        {"mark": {"type": "line", "color": "#b3c0b1", "strokeWidth": 1.6},
         "encoding": {**PC_BASE, "detail": {"field": "state"}, "order": {"field": "axis_i"}}},
        {"mark": {"type": "point", "filled": True, "size": 34, "color": "#a7b5a5"},
         "encoding": {**PC_BASE, "tooltip": [{"field": "state_name", "title": "State"}, {"field": "axis", "title": "Activity"},
                                             {"field": "rate", "title": "% of adults"}]}},
        # the highlighted state, drawn on top
        {"transform": [{"filter": "datum.on"}],
         "mark": {"type": "line", "color": OCHRE, "strokeWidth": 4},
         "encoding": {**PC_BASE, "order": {"field": "axis_i"}}},
        {"transform": [{"filter": "datum.on"}],
         "mark": {"type": "point", "filled": True, "size": 110, "color": OCHRE, "stroke": "white", "strokeWidth": 1.5},
         "encoding": {**PC_BASE, "tooltip": [{"field": "state_name", "title": "State"}, {"field": "axis", "title": "Activity"},
                                             {"field": "rate", "title": "% of adults"}]}},
        {"transform": [{"filter": "datum.on"}, {"calculate": "format(datum.rate, '.1f') + '%'", "as": "lab"}],
         "mark": {"type": "text", "align": "left", "dx": 10, "fontSize": 13, "fontWeight": 700, "color": INK},
         "encoding": {**PC_BASE, "text": {"field": "lab"}}},
        # axis ends: 0% at the bottom, the leading state at the top
        {"transform": [{"aggregate": [{"op": "max", "field": "hi", "as": "hi"}], "groupby": ["axis"]},
                       {"fold": ["hi"], "as": ["end", "v"]},
                       {"calculate": "'Top ' + format(datum.v, '.1f') + '%'", "as": "lab"}],
         "mark": {"type": "text", "align": "center", "dy": -13, "fontSize": 11, "color": MUTED},
         "encoding": {"y": {"datum": 1}, "text": {"field": "lab"}}},
        {"transform": [{"aggregate": [{"op": "count", "as": "n"}], "groupby": ["axis"]}],
         "mark": {"type": "text", "align": "center", "dy": 14, "fontSize": 11, "color": MUTED},
         "encoding": {"y": {"datum": 0}, "text": {"value": "0%"}}}
    ],
    "config": {"padding": {"left": 30, "right": 50, "top": 10, "bottom": 24}}
})

print("specs written")
