// Builds the GitHub activity cards for the profile README.
// Run by .github/workflows/profile-stats.yml. Node 20+, no dependencies.
//
// Env:
//   GH_TOKEN  token for the GitHub GraphQL API (GITHUB_TOKEN works; a personal
//             token in the METRICS_TOKEN secret adds private contributions)
//   USERNAME  GitHub login to read
//   OUT       output folder (default: generated)
//   MOCK      optional path to a JSON file of sample data, for local previews
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const USER = process.env.USERNAME || 'C221213-Maisha';
const OUT = process.env.OUT || 'generated';
const TOKEN = process.env.GH_TOKEN;

// ------------------------------------------------------------------ themes
// Navy and gold to match the header. Contribution levels use one blue ramp
// (sequential). Gold is kept for highlights only. Language colors are a
// validated categorical palette in fixed order.
const THEMES = {
  light: {
    card: '#F6F8FA', border: '#D0D7DE', text: '#1F2328', muted: '#59636E',
    title: '#2C3E50', accent: '#B7950B', grid: '#E7E7E7', axis: '#C2C2C2',
    empty: '#E4E9EF', levels: ['#9DC8F7', '#519CED', '#2370CD', '#0E3D7E'],
    series: '#2370CD', area: '#2370CD',
    cats: ['#257DE0', '#F47230', '#00B894', '#F2A600', '#EE7FAC', '#008A17'], other: '#9C9C9C',
    plane: '#2C3E50',
  },
  dark: {
    card: '#161B22', border: '#30363D', text: '#E6EDF3', muted: '#8B949E',
    title: '#9DB7D5', accent: '#D4AC0D', grid: '#262C34', axis: '#474747',
    empty: '#1F2630', levels: ['#0F4A96', '#1B64BE', '#338CED', '#84B9F3'],
    series: '#338CED', area: '#338CED',
    cats: ['#338CED', '#E76624', '#00A888', '#D28E05', '#E24D8B', '#0AAC23'], other: '#6B6B6B',
    plane: '#E6EDF3',
  },
};
const FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";
const MONO = 'ui-monospace,SFMono-Regular,Menlo,Consolas,monospace';
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fmt = (n) => n.toLocaleString('en-US');
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const fdate = (d) => { const [y, m, day] = d.split('-'); return `${MONTHS[+m - 1]} ${+day}, ${y}`; };
const REDUCE = '@media (prefers-reduced-motion:reduce){*{animation:none!important}.in{opacity:1}}';

// ------------------------------------------------------------------ data
async function gql(query, variables) {
  const res = await fetch('https://api.github.com/graphql', {
    method: 'POST',
    headers: { Authorization: `bearer ${TOKEN}`, 'Content-Type': 'application/json', 'User-Agent': 'profile-stats' },
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (!res.ok || json.errors) throw new Error(JSON.stringify(json.errors || json));
  return json.data;
}

async function fetchData() {
  const base = await gql(`query($login:String!){ user(login:$login){
    createdAt followers{totalCount}
    pullRequests{totalCount} issues{totalCount}
  } }`, { login: USER });
  const u = base.user;

  // Repositories (owned, not forks), paged
  const repos = [];
  let after = null;
  do {
    const d = await gql(`query($login:String!,$after:String){ user(login:$login){
      repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100,after:$after){
        totalCount pageInfo{hasNextPage endCursor}
        nodes{ name stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}} }
      } } }`, { login: USER, after });
    const r = d.user.repositories;
    repos.push(...r.nodes);
    after = r.pageInfo.hasNextPage ? r.pageInfo.endCursor : null;
  } while (after);

  // Contribution calendar for every year since the account was created
  const days = [];
  let commitsThisYear = 0;
  const startYear = new Date(u.createdAt).getUTCFullYear();
  const now = new Date();
  for (let y = startYear; y <= now.getUTCFullYear(); y++) {
    const from = new Date(Date.UTC(y, 0, 1)).toISOString();
    const to = y === now.getUTCFullYear() ? now.toISOString() : new Date(Date.UTC(y, 11, 31, 23, 59, 59)).toISOString();
    const d = await gql(`query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){
      contributionsCollection(from:$from,to:$to){ totalCommitContributions
        contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } } } }`,
      { login: USER, from, to });
    const c = d.user.contributionsCollection;
    if (y === now.getUTCFullYear()) commitsThisYear = c.totalCommitContributions;
    for (const w of c.contributionCalendar.weeks) for (const day of w.contributionDays) days.push(day);
  }
  const seen = new Set();
  const calendar = days.filter((d) => !seen.has(d.date) && seen.add(d.date)).sort((a, b) => a.date.localeCompare(b.date))
    .map((d) => ({ date: d.date, count: d.contributionCount }));

  const langs = {};
  for (const r of repos) for (const e of r.languages.edges) langs[e.node.name] = (langs[e.node.name] || 0) + e.size;

  return {
    calendar, commitsThisYear, languages: langs,
    prs: u.pullRequests.totalCount, issues: u.issues.totalCount, followers: u.followers.totalCount,
    repos: repos.length, stars: repos.reduce((s, r) => s + r.stargazerCount, 0),
  };
}

// ------------------------------------------------------------------ derived numbers
function derive(data) {
  const cal = data.calendar;
  const total = cal.reduce((s, d) => s + d.count, 0);
  const last365 = cal.slice(-365);
  const activeDays = last365.filter((d) => d.count > 0).length;
  // Streaks. Today with no contributions yet does not break the current streak.
  let longest = { len: 0, start: null, end: null }, run = { len: 0, start: null };
  for (const d of cal) {
    if (d.count > 0) { if (!run.len) run.start = d.date; run.len++; if (run.len > longest.len) longest = { len: run.len, start: run.start, end: d.date }; }
    else run = { len: 0, start: null };
  }
  let i = cal.length - 1;
  if (i >= 0 && cal[i].count === 0) i--;
  let current = { len: 0, start: null, end: null };
  if (i >= 0 && cal[i].count > 0) {
    current.end = cal[i].date;
    while (i >= 0 && cal[i].count > 0) { current.len++; current.start = cal[i].date; i--; }
  }
  const langTotal = Object.values(data.languages).reduce((s, v) => s + v, 0) || 1;
  const sorted = Object.entries(data.languages).sort((a, b) => b[1] - a[1]);
  const top = sorted.slice(0, 6).map(([name, size]) => ({ name, pct: (size / langTotal) * 100 }));
  const rest = sorted.slice(6).reduce((s, [, v]) => s + v, 0);
  if (rest > 0) top.push({ name: 'Other', pct: (rest / langTotal) * 100, other: true });
  return { ...data, total, activeDays, longest, current, top, first: cal.find((d) => d.count > 0)?.date || cal[0]?.date };
}

// ------------------------------------------------------------------ cards
const frame = (W, H, T, label, style, body) => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}">
<style>text{font-family:${FONT}}.h{font-size:15px;font-weight:600;fill:${T.title}}.l{font-size:13px;fill:${T.muted}}.v{font-size:13px;font-weight:600;fill:${T.text}}
.in{opacity:0;animation:in .6s cubic-bezier(.2,.7,.2,1) forwards}@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
${style}${REDUCE}</style>
<rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="14" fill="${T.card}" stroke="${T.border}"/>
${body}</svg>
`;

function statsCard(s, T) {
  const W = 495, H = 200;
  const rows = [
    ['Total contributions', fmt(s.total)],
    [`Commits in ${new Date().getUTCFullYear()}`, fmt(s.commitsThisYear)],
    ['Pull requests', fmt(s.prs)],
    ['Issues', fmt(s.issues)],
    ['Public repositories', fmt(s.repos)],
    ['Stars earned', fmt(s.stars)],
  ];
  const body = rows.map(([k, v], i) => `<g class="in" style="animation-delay:${(0.1 + i * 0.1).toFixed(2)}s">
<rect x="28" y="${55 + i * 22}" width="3" height="12" rx="1.5" fill="${T.accent}"/>
<text x="40" y="${66 + i * 22}" class="l">${esc(k)}</text><text x="285" y="${66 + i * 22}" text-anchor="end" class="v">${esc(v)}</text></g>`).join('');
  const r = 50, cx = 395, cy = 112, C = 2 * Math.PI * r, frac = s.activeDays / 365;
  const ring = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${T.empty}" stroke-width="8"/>
<circle class="arc" cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${T.accent}" stroke-width="8" stroke-linecap="round" stroke-dasharray="${C.toFixed(1)}" stroke-dashoffset="${C.toFixed(1)}" transform="rotate(-90 ${cx} ${cy})"/>
<text x="${cx}" y="${cy + 2}" text-anchor="middle" style="font-size:26px;font-weight:700;fill:${T.text}" class="in" >${s.activeDays}</text>
<text x="${cx}" y="${cy + 20}" text-anchor="middle" class="l in" style="font-size:11px">active days</text>
<text x="${cx}" y="${cy + 76}" text-anchor="middle" class="l" style="font-size:11px">in the last 365</text>`;
  const style = `.arc{animation:arc 1.4s .3s cubic-bezier(.2,.7,.2,1) forwards}@keyframes arc{to{stroke-dashoffset:${(C * (1 - frac)).toFixed(1)}}}`;
  return frame(W, H, T, `GitHub stats: ${s.total} total contributions, ${s.commitsThisYear} commits this year, ${s.prs} pull requests, ${s.issues} issues, ${s.repos} public repositories, ${s.stars} stars, ${s.activeDays} active days in the last 365.`,
    style, `<text x="28" y="36" class="h">GitHub stats</text>${body}${ring}`);
}

function langCard(s, T) {
  const W = 495, H = 200, bx = 28, bw = W - 56, by = 54;
  let x = bx;
  const segs = s.top.map((l, i) => {
    const w = Math.max(2, (l.pct / 100) * bw - 2);
    const col = l.other ? T.other : T.cats[i];
    const seg = `<rect class="seg" style="animation-delay:${(0.15 + i * 0.08).toFixed(2)}s" x="${x.toFixed(1)}" y="${by}" width="${w.toFixed(1)}" height="10" rx="2" fill="${col}"/>`;
    x += w + 2;
    return seg;
  }).join('');
  const list = s.top.map((l, i) => {
    const col = l.other ? T.other : T.cats[i];
    const cx = bx + (i % 2) * 225, cy = 100 + Math.floor(i / 2) * 26;
    return `<g class="in" style="animation-delay:${(0.4 + i * 0.08).toFixed(2)}s"><circle cx="${cx + 5}" cy="${cy - 4}" r="5" fill="${col}"/>
<text x="${cx + 18}" y="${cy}" class="v">${esc(l.name)}</text><text x="${cx + 205}" y="${cy}" text-anchor="end" class="l">${l.pct.toFixed(1)}%</text></g>`;
  }).join('');
  const style = `.seg{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow .7s cubic-bezier(.2,.7,.2,1) forwards}@keyframes grow{to{transform:scaleX(1)}}`;
  return frame(W, H, T, 'Most used languages: ' + s.top.map((l) => `${l.name} ${l.pct.toFixed(1)}%`).join(', '),
    style, `<text x="28" y="36" class="h">Most used languages</text>${segs}${list}`);
}

function streakCard(s, T) {
  const W = 1000, H = 170;
  const range = (a, b) => (a ? (a === b ? fdate(a) : `${fdate(a)} to ${fdate(b)}`) : 'No streak yet');
  const cells = [
    [fmt(s.total), 'Total contributions', s.first ? `${fdate(s.first)} to present` : ''],
    [String(s.current.len), 'Current streak', range(s.current.start, s.current.end)],
    [String(s.longest.len), 'Longest streak', range(s.longest.start, s.longest.end)],
  ];
  const body = cells.map(([big, lab, sub], i) => {
    const x = 167 + i * 333;
    const sep = i ? `<line x1="${i * 333}" y1="30" x2="${i * 333}" y2="140" stroke="${T.border}"/>` : '';
    const ring = i === 1 ? `<circle cx="${x}" cy="66" r="38" fill="none" stroke="${T.empty}" stroke-width="5"/>
<circle class="spin" cx="${x}" cy="66" r="38" fill="none" stroke="${T.accent}" stroke-width="5" stroke-linecap="round" stroke-dasharray="60 179"/>` : '';
    return `${sep}${ring}<g class="in" style="animation-delay:${(0.1 + i * 0.15).toFixed(2)}s">
<text x="${x}" y="${i === 1 ? 77 : 74}" text-anchor="middle" style="font-size:${i === 1 ? 30 : 32}px;font-weight:700;fill:${i === 1 ? T.text : T.title}">${esc(big)}</text>
<text x="${x}" y="128" text-anchor="middle" class="v" style="font-size:14px">${esc(lab)}</text>
<text x="${x}" y="148" text-anchor="middle" class="l" style="font-size:12px">${esc(sub)}</text></g>`;
  }).join('');
  const style = `.spin{transform-origin:500px 66px;transform-box:view-box;animation:spin 6s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}`;
  return frame(W, H, T, `Total contributions ${s.total}. Current streak ${s.current.len} days. Longest streak ${s.longest.len} days.`, style, body);
}

function activityCard(s, T) {
  const W = 1000, H = 300, L = 56, R = 28, top = 80, bot = 250;
  const days = s.calendar.slice(-31);
  const max = Math.max(4, ...days.map((d) => d.count));
  const step = Math.ceil(max / 4);
  const ymax = step * 4;
  const xs = (i) => L + (i * (W - L - R)) / (days.length - 1);
  const ys = (v) => bot - (v / ymax) * (bot - top);
  const grid = [0, 1, 2, 3, 4].map((k) => `<line x1="${L}" y1="${ys(k * step)}" x2="${W - R}" y2="${ys(k * step)}" stroke="${k ? T.grid : T.axis}"/>
<text x="${L - 10}" y="${ys(k * step) + 4}" text-anchor="end" class="l" style="font-size:11px">${k * step}</text>`).join('');
  const xl = days.map((d, i) => (i % 5 === 0 || i === days.length - 1)
    ? `<text x="${xs(i)}" y="${bot + 20}" text-anchor="middle" class="l" style="font-size:11px">${esc(MONTHS[+d.date.slice(5, 7) - 1] + ' ' + +d.date.slice(8))}</text>` : '').join('');
  const pts = days.map((d, i) => `${xs(i).toFixed(1)},${ys(d.count).toFixed(1)}`);
  const line = `M${pts.join(' L')}`;
  const area = `${line} L${xs(days.length - 1).toFixed(1)},${bot} L${L},${bot} Z`;
  let len = 0;
  for (let i = 1; i < days.length; i++) len += Math.hypot(xs(i) - xs(i - 1), ys(days[i].count) - ys(days[i - 1].count));
  const mi = days.reduce((b, d, i) => (d.count > days[b].count ? i : b), 0);
  const peak = days[mi].count ? `<g class="in" style="animation-delay:1.6s"><circle cx="${xs(mi)}" cy="${ys(days[mi].count)}" r="5" fill="${T.accent}" stroke="${T.card}" stroke-width="2"/>
<text x="${xs(mi)}" y="${ys(days[mi].count) - 12}" text-anchor="middle" class="v" style="font-size:12px">${days[mi].count} on ${esc(MONTHS[+days[mi].date.slice(5, 7) - 1] + ' ' + +days[mi].date.slice(8))}</text></g>` : '';
  const style = `.ln{fill:none;stroke:${T.series};stroke-width:2;stroke-linejoin:round;stroke-dasharray:${len.toFixed(0)};stroke-dashoffset:${len.toFixed(0)};animation:draw 1.6s cubic-bezier(.4,0,.2,1) forwards}
.ar{opacity:0;animation:fade 1s 1s ease-out forwards}@keyframes draw{to{stroke-dashoffset:0}}@keyframes fade{to{opacity:1}}`;
  return frame(W, H, T, `Contributions per day over the last 31 days, peaking at ${days[mi].count}.`, style,
    `<defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${T.area}" stop-opacity=".22"/><stop offset="1" stop-color="${T.area}" stop-opacity="0"/></linearGradient></defs>
<text x="28" y="36" class="h">Contributions, last 31 days</text>${grid}${xl}<path class="ar" d="${area}" fill="url(#ag)"/><path class="ln" d="${line}"/>${peak}`);
}

// Paper plane flying over the last year of contributions. Each square it
// passes lights up gold, then settles to its contribution level.
function planeCard(s, T) {
  const W = 1000, H = 210, cell = 13, gap = 3, ox = 92, oy = 52, DUR = 14;
  const cal = s.calendar.slice(-371);
  // align to weeks: first column starts on the weekday of the first day
  const firstDow = new Date(cal[0].date + 'T00:00:00Z').getUTCDay();
  const max = Math.max(1, ...cal.map((d) => d.count));
  const level = (c) => (c === 0 ? -1 : Math.min(3, Math.floor((c / max) * 4 - 1e-9)));
  const cols = Math.ceil((cal.length + firstDow) / 7);
  const travel = DUR * 0.8;
  const cells = [], months = [];
  let lastM = -1;
  cal.forEach((d, i) => {
    const k = i + firstDow, c = Math.floor(k / 7), r = k % 7;
    const x = ox + c * (cell + gap), y = oy + r * (cell + gap);
    const lv = level(d.count);
    const m = +d.date.slice(5, 7) - 1;
    if (r === 0 && m !== lastM && c < cols - 1) { months.push(`<text x="${x}" y="${oy - 10}" class="l" style="font-size:11px">${MONTHS[m]}</text>`); lastM = m; }
    if (lv < 0) cells.push(`<rect x="${x}" y="${y}" width="${cell}" height="${cell}" rx="3" fill="${T.empty}"/>`);
    else {
      const delay = 0.6 + (c / cols) * travel;
      cells.push(`<rect class="c c${lv}" style="animation-delay:${delay.toFixed(2)}s" x="${x}" y="${y}" width="${cell}" height="${cell}" rx="3"><title>${d.count} on ${d.date}</title></rect>`);
    }
  });
  const gw = cols * (cell + gap);
  // flight path: weaves across the grid, then climbs out to the right
  const pts = [];
  for (let k = 0; k <= 24; k++) {
    const x = ox - 30 + (k / 24) * (gw + 40);
    const y = oy + 3.5 * (cell + gap) + Math.sin(k * 0.9) * 2.6 * (cell + gap);
    pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }
  const path = `M${ox - 60},${oy + 120} Q${ox - 50},${oy + 60} ${pts[0]} T${pts.slice(1).join(' T')} T${Math.min(W - 24, ox + gw + 20)},${oy - 26}`;
  const lvlStyle = T.levels.map((c, i) => `.c${i}{--f:${c}}`).join('');
  const style = `.c{fill:${T.empty};animation:lit ${DUR}s linear infinite}${lvlStyle}
@keyframes lit{0%,5%{fill:${T.accent}}5.5%,88%{fill:var(--f)}88.5%,100%{fill:${T.empty}}}
.trail{fill:none;stroke:${T.accent};stroke-width:1.5;stroke-dasharray:3 6;opacity:.55}
.legend{font-size:11px;fill:${T.muted}}`;
  const legend = `<text x="${ox + gw - 150}" y="${H - 14}" class="legend">Less</text>` +
    [T.empty, ...T.levels].map((c, i) => `<rect x="${ox + gw - 120 + i * 17}" y="${H - 25}" width="13" height="13" rx="3" fill="${c}"/>`).join('') +
    `<text x="${ox + gw - 12}" y="${H - 14}" class="legend">More</text>`;
  const days = ['', 'Mon', '', 'Wed', '', 'Fri', ''].map((d, r) => d ? `<text x="${ox - 10}" y="${oy + r * (cell + gap) + 10}" text-anchor="end" class="l" style="font-size:11px">${d}</text>` : '').join('');
  const plane = `<g><path d="M-11,-8 L13,0 L-11,8 L-6,0 Z" fill="${T.plane}"/><path d="M-6,0 L13,0 L-11,8 Z" fill="${T.accent}"/>
<animateMotion dur="${DUR}s" repeatCount="indefinite" rotate="auto" keyPoints="0;0.04;0.96;1" keyTimes="0;0.04;0.86;1" calcMode="linear" path="${path}"/>
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.03;0.9;0.95;1" dur="${DUR}s" repeatCount="indefinite"/></g>`;
  return frame(W, H, T, `Contribution calendar for the last year with a paper plane flying across it. ${s.calendar.slice(-365).reduce((a, d) => a + d.count, 0)} contributions in the last 365 days.`,
    style, `<text x="28" y="30" class="h">A year of contributions</text>${months.join('')}${days}${cells.join('')}
<path class="trail" d="${path}"/>${plane}${legend}`);
}

// Milestones: six achievements, each with three tiers.
function milestoneCard(s, T) {
  const W = 1000, H = 160;
  const items = [
    ['Contributions', s.total, [100, 500, 1000]],
    ['Commits this year', s.commitsThisYear, [50, 250, 500]],
    ['Repositories', s.repos, [5, 15, 30]],
    ['Longest streak', s.longest.len, [7, 30, 100]],
    ['Active days', s.activeDays, [30, 100, 200]],
    ['Stars earned', s.stars, [5, 25, 100]],
  ];
  const cw = W / items.length;
  const body = items.map(([lab, v, tiers], i) => {
    const x = cw * i + cw / 2, tier = tiers.filter((t) => v >= t).length;
    const hex = [0, 60, 120, 180, 240, 300].map((a) => { const r = 36, t = (a - 90) * Math.PI / 180; return `${(x + r * Math.cos(t)).toFixed(1)},${(58 + r * Math.sin(t)).toFixed(1)}`; }).join(' ');
    const pips = [0, 1, 2].map((p) => `<circle cx="${x - 12 + p * 12}" cy="138" r="3.5" fill="${p < tier ? T.accent : T.empty}"/>`).join('');
    return `<g class="pop" style="animation-delay:${(0.1 + i * 0.12).toFixed(2)}s">
<polygon points="${hex}" fill="none" stroke="${tier ? T.accent : T.border}" stroke-width="2"/>
<text x="${x}" y="64" text-anchor="middle" style="font-size:18px;font-weight:700;fill:${T.text}">${esc(v >= 1000 ? (v / 1000).toFixed(1).replace(/\.0$/, '') + 'k' : String(v))}</text>
<text x="${x}" y="116" text-anchor="middle" class="l" style="font-size:12.5px">${esc(lab)}</text>${pips}</g>`;
  }).join('');
  const style = `.pop{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .6s cubic-bezier(.2,.7,.2,1.3) forwards}@keyframes pop{from{opacity:0;transform:scale(.7)}to{opacity:1;transform:none}}`;
  return frame(W, H, T, 'Milestones: ' + items.map(([l, v]) => `${l} ${v}`).join(', '), style, body);
}

// ------------------------------------------------------------------ main
const raw = process.env.MOCK ? JSON.parse(readFileSync(process.env.MOCK, 'utf8')) : await fetchData();
const s = derive(raw);
mkdirSync(OUT, { recursive: true });
const cards = { stats: statsCard, languages: langCard, streak: streakCard, activity: activityCard, contributions: planeCard, milestones: milestoneCard };
for (const [name, fn] of Object.entries(cards)) {
  for (const [t, T] of Object.entries(THEMES)) {
    writeFileSync(join(OUT, `${name}-${t}.svg`), fn(s, T));
  }
}
console.log(`Wrote ${Object.keys(cards).length * 2} cards to ${OUT}: ${s.total} contributions, streak ${s.current.len}, longest ${s.longest.len}`);
