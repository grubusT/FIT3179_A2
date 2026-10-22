/* Learning Outside: loads each Vega-Lite spec into its figure.
   Keys are the ids of <figure class="viz"> elements in index.html. */
const charts = {
  'viz-waffle':     'specs/waffle_outdoor_play.vg.json',
  'viz-screens':    'specs/screens_vs_outdoors.vg.json',
  'viz-choropleth': 'specs/protected_choropleth.vg.json',
  'viz-parks':      'specs/parks_point_map.vg.json',
  'viz-symbol':     'specs/bushwalking_symbol_map.vg.json',
  'viz-parallel':   'specs/state_parallel_coordinates.vg.json',
  'viz-bump':       'specs/activity_rank_bump.vg.json',
  'viz-heatmap':    'specs/activity_age_heatmap.vg.json',
  'viz-dumbbell':   'specs/gender_dumbbell.vg.json',
  'viz-motives':    'specs/motivations_bar.vg.json',
  'viz-places':     'specs/places_small_multiples.vg.json',
  'viz-vce':        'specs/vce_enrolments_line.vg.json',
  'viz-gender':     'specs/vce_gender_diverging.vg.json',
  'viz-gaps':       'specs/participation_gaps.vg.json'
};

/* Shared theme so every chart matches the page typography and colours */
const theme = {
  font: 'Figtree, system-ui, sans-serif',
  background: null,
  view: { stroke: null },
  title: { font: 'Zilla Slab, Georgia, serif', fontSize: 18, fontWeight: 600, color: '#1f3b2d', anchor: 'start' },
  axis: {
    labelColor: '#4b5b51', titleColor: '#4b5b51', labelFontSize: 12, titleFontSize: 12, titleFontWeight: 500,
    labelFont: 'Figtree, sans-serif', titleFont: 'Figtree, sans-serif',
    gridColor: '#dbe3d6', domainColor: '#b9c7b6', tickColor: '#b9c7b6'
  },
  legend: { labelColor: '#4b5b51', titleColor: '#1e2b24', labelFontSize: 12, titleFontSize: 12, titleFontWeight: 600 },
  header: { labelFont: 'Figtree, sans-serif' },
  text: { font: 'Figtree, sans-serif', color: '#1e2b24' }
};

const views = {};
window.chartViews = views; // handy for debugging in the browser console

/* On narrow screens (phones), adapt specs so labels stay readable:
   small multiples stack in one column, legends move under the chart,
   maps lose spare height, and the italic annotations (which need room) are dropped. */
function isNote(layer) {
  return layer && layer.mark && layer.mark.type === 'text' && layer.mark.fontStyle === 'italic';
}
function dropNotes(view) {
  if (!view || !Array.isArray(view.layer)) return;
  view.layer = view.layer.filter(l => !isNote(l));
  view.layer.forEach(dropNotes);
}

function fitToScreen(spec, slotWidth, id) {
  if (window.innerWidth >= 720) return spec;  // phones only; judged on the screen, not the column
  const shrink = (view) => {
    if (view && typeof view.width === 'number') view.width = Math.max(180, Math.min(view.width, slotWidth - 205));
  };
  if (spec.columns) spec.columns = 1;
  if (spec.facet && spec.facet.column) spec.facet = { row: spec.facet.column };
  shrink(spec.spec);
  (spec.vconcat || []).forEach(shrink);
  dropNotes(spec);
  (spec.vconcat || []).forEach(dropNotes);
  if (spec.config && spec.config.legend && spec.config.legend.orient === 'right') {
    spec.config.legend.orient = 'bottom';
    spec.config.legend.direction = 'vertical';
  }
  if (spec.projection && typeof spec.height === 'number') spec.height = Math.round(slotWidth * 0.85);
  (spec.layer || []).forEach(l => {
    const legend = l.encoding && l.encoding.color && l.encoding.color.legend;
    if (legend && legend.orient === 'none') {  // a hand-placed legend goes under the map on phones
      legend.orient = 'bottom'; legend.direction = 'vertical';
      delete legend.legendX; delete legend.legendY;
    }
  });
  if (id === 'viz-parallel' || id === 'viz-bump' || id === 'viz-heatmap') {
    const axis = spec.encoding.x.axis || (spec.encoding.x.axis = {});
    Object.assign(axis, { labelAngle: -45, labelAlign: 'left', labelBaseline: 'middle' });
    if (id === 'viz-parallel') spec.layer = spec.layer.filter(l => !(l.mark && l.mark.dy === -13));
    if (spec.config && spec.config.padding) spec.config.padding.right = 80;
  }
  return spec;
}

async function embed(id, url) {
  const slot = document.querySelector(`#${id} .viz-slot`);
  if (!slot) return;
  try {
    const spec = fitToScreen(await (await fetch(url)).json(), slot.clientWidth, id);
    const result = await vegaEmbed(slot, spec, { actions: false, config: theme, renderer: 'svg' });
    slot.classList.add('is-live');
    views[id] = result.view;
  } catch (err) {
    slot.classList.add('is-error');
    slot.textContent = 'This chart could not load. Please refresh the page.';
    console.error(`Could not load ${url}:`, err);
  }
}

/* Clicking a state on the bushwalking map highlights it in the parallel coordinates */
function linkMapToProfiles() {
  const map = views['viz-symbol'];
  const pc = views['viz-parallel'];
  if (!map || !pc) return;
  map.addSignalListener('pickState', (name, value) => {
    const state = value && value.state && value.state[0];
    if (state) pc.signal('hl', state).runAsync();
  });
}

Promise.all(Object.entries(charts).map(([id, url]) => embed(id, url)))
  .then(linkMapToProfiles);
