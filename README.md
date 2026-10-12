# Learning outside

A data story about outdoor education and learning in nature across Australia.

- **Live page:** https://YOUR-USERNAME.github.io/REPO-NAME/
- **Sketch:** [sketch.pdf](sketch.pdf)

## Structure

```
index.html       the page
css/style.css    all styling: palette, type scale, layout grid
js/main.js       loads each Vega-Lite spec into its placeholder, with a shared chart theme
specs/           one Vega-Lite spec per chart (*.vg.json)
data/            cleaned CSV and TopoJSON files used by the specs
assets/          illustrations drawn in code (the hero scene is inline in index.html)
tools/           Python scripts used to clean the data, build the specs and draw the illustrations
```

## Charts (14)

| # | Chart | Idiom | Data |
|---|---|---|---|
| 1 | Children who play outdoors most days | Isotype waffle | RCH poll |
| 2 | Screens vs outdoors by age | Slope (line) chart | RCH poll |
| 3 | % of each state's land protected | Choropleth map | CAPAD 2024 |
| 4 | Protected areas by manager | Dot map (uniform dots, colour by category) | CAPAD 2024 |
| 5 | Bushwalkers by state | Proportional symbol map | AusPlay states |
| 6 | State outdoor profiles | Parallel coordinates | AusPlay states |
| 7 | Activity rank by age | Bump chart | AusPlay national |
| 8 | Outdoor activity by age | Heatmap | AusPlay national |
| 9 | Women vs men | Dumbbell chart | AusPlay national |
| 10 | Reasons for being active | Radial bar chart | AusPlay national |
| 11 | Where people are active | Small multiples (bar) | AusPlay national |
| 12 | VCE Outdoor and Environmental Studies enrolments | Annotated line chart | VCAA |
| 13 | Boys vs girls in VCE OES | Diverging bar chart | VCAA |
| 14 | Weekly activity by income, education, disability, First Nations | Small multiples (bar) | AusPlay national |

Interactions: clicking a state on the bushwalking map highlights it in the parallel coordinates. The radial chart and parallel coordinates have dropdowns, the point map and VCE chart filter from their legends, and the bump chart highlights a line on hover. Every chart has tooltips.

The categorical colours were checked for colour-blind separation with a palette validator.

## Data sources

- Australian Sports Commission, AusPlay national and state data tables, 2024 to 2025
- DCCEEW, Collaborative Australian Protected Areas Database (CAPAD) 2024
- VCAA, VCE Unit Completion Outcomes: Outdoor and Environmental Studies, 2014 to 2025
- Royal Children's Hospital, National Child Health Poll 28: How we play, 2022
- Geoscience Australia, Area of Australia: states and territories (land area for % protected)
- Natural Earth, Admin 1 states and provinces 1:50m (public domain), simplified with mapshaper

## AI acknowledgement

Generative AI (Claude, Anthropic) was used to help with data cleaning, page layout and CSS.
