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
  'viz-radial':     'specs/motivations_radial.vg.json',
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

async function embed(id, spec) {
  const slot = document.querySelector(`#${id} .viz-slot`);
  if (!slot) return;
  try {
    const result = await vegaEmbed(slot, spec, { actions: false, config: theme, renderer: 'svg' });
    slot.classList.add('is-live');
    views[id] = result.view;
  } catch (err) {
    slot.classList.add('is-error');
    slot.textContent = 'This chart could not load. Please refresh the page.';
    console.error(`Could not load ${spec}:`, err);
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

Promise.all(Object.entries(charts).map(([id, spec]) => embed(id, spec)))
  .then(linkMapToProfiles);
