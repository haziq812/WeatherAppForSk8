/* ============================================================
   Sk8 Weather Planner – Frontend JavaScript
   ============================================================ */

// Map OpenWeatherMap condition codes to emojis
function conditionEmoji(id) {
  if (id >= 200 && id < 300) return '⛈️';
  if (id >= 300 && id < 400) return '🌦️';
  if (id >= 500 && id < 600) return '🌧️';
  if (id >= 600 && id < 700) return '❄️';
  if (id >= 700 && id < 800) return '🌫️';
  if (id === 800)             return '☀️';
  if (id === 801)             return '🌤️';
  if (id === 802)             return '⛅';
  if (id >= 803)              return '☁️';
  return '🌡️';
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T12:00:00');
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

function badgeClass(badge) {
  return `skate-badge badge-${badge}`;
}

// ---- WEATHER ----

async function fetchWeather() {
  const city   = document.getElementById('cityInput').value.trim();
  const apiKey = document.getElementById('apiKeyInput').value.trim();
  const errEl  = document.getElementById('weatherError');

  errEl.classList.add('hidden');
  if (!city) { showError(errEl, 'Please enter a city name.'); return; }
  if (!apiKey) { showError(errEl, 'Please enter your OpenWeatherMap API key.'); return; }

  const btn = document.getElementById('searchBtn');
  btn.innerHTML = '<span class="spinner"></span>Loading…';
  btn.disabled = true;

  try {
    const resp = await fetch(`/api/weather?city=${encodeURIComponent(city)}&api_key=${encodeURIComponent(apiKey)}`);
    const data = await resp.json();

    if (!resp.ok) {
      showError(errEl, data.error || 'Failed to fetch weather data.');
      return;
    }

    renderCurrent(data.current);
    renderForecast(data.forecast);

  } catch (e) {
    showError(errEl, 'Network error. Please try again.');
  } finally {
    btn.innerHTML = 'Get Forecast';
    btn.disabled = false;
  }
}

function renderCurrent(c) {
  const section = document.getElementById('currentSection');
  section.classList.remove('hidden');

  document.getElementById('cityName').textContent = c.name + (c.sys?.country ? `, ${c.sys.country}` : '');
  const condId = c.weather?.[0]?.id ?? 800;
  document.getElementById('currentIcon').textContent   = conditionEmoji(condId);
  document.getElementById('currentDesc').textContent   = c.weather?.[0]?.description ?? '';
  document.getElementById('currentTemp').textContent   = `${c.temp_c}°C / ${c.temp_f}°F`;
  document.getElementById('currentHumidity').textContent = `${c.main?.humidity ?? '–'}%`;
  document.getElementById('currentWind').textContent   = `${(c.wind?.speed ?? 0).toFixed(1)} m/s`;

  const badge = document.getElementById('currentBadge');
  badge.textContent  = `${c.skate.label} (${c.skate.score}/100)`;
  badge.className    = badgeClass(c.skate.badge);

  const reasonsEl = document.getElementById('currentReasons');
  reasonsEl.innerHTML = c.skate.reasons.map(r => `<span class="reason-tag">${r}</span>`).join('');
}

function renderForecast(days) {
  const section = document.getElementById('forecastSection');
  const grid    = document.getElementById('forecastGrid');
  section.classList.remove('hidden');
  grid.innerHTML = '';

  days.forEach(day => {
    const condId = day.weather?.[0]?.id ?? 800;
    const card = document.createElement('div');
    card.className = 'forecast-card';
    card.innerHTML = `
      <div class="forecast-date">${formatDate(day.dt_txt?.slice(0,10))}</div>
      <div class="forecast-icon">${conditionEmoji(condId)}</div>
      <div class="forecast-desc">${day.weather?.[0]?.description ?? ''}</div>
      <div class="forecast-temp">${day.temp_c}°C</div>
      <div class="forecast-skate ${badgeClass(day.skate.badge)}">${day.skate.label}</div>
    `;
    grid.appendChild(card);
  });
}

// ---- SESSION PLANNER ----

async function loadSessions() {
  const resp = await fetch('/api/sessions');
  const sessions = await resp.json();
  renderSessions(sessions);
}

function renderSessions(sessions) {
  const list = document.getElementById('sessionList');
  if (!sessions.length) {
    list.innerHTML = '<p class="no-sessions">No sessions planned yet. Add one above!</p>';
    return;
  }
  list.innerHTML = sessions.map(s => `
    <div class="session-item" id="session-${s.id}">
      <span class="session-date">${formatDate(s.date)}</span>
      <span class="session-location">📍 ${escapeHtml(s.location)}</span>
      <span class="session-notes">${escapeHtml(s.notes || '')}</span>
      <button class="session-delete" onclick="deleteSession(${s.id})">✕ Remove</button>
    </div>
  `).join('');
}

async function addSession(event) {
  event.preventDefault();
  const errEl    = document.getElementById('sessionError');
  const date     = document.getElementById('sessionDate').value;
  const location = document.getElementById('sessionLocation').value.trim();
  const notes    = document.getElementById('sessionNotes').value.trim();

  errEl.classList.add('hidden');

  try {
    const resp = await fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date, location, notes }),
    });
    if (!resp.ok) {
      const d = await resp.json();
      showError(errEl, d.error || 'Failed to add session.');
      return;
    }
    document.getElementById('sessionForm').reset();
    await loadSessions();
  } catch (e) {
    showError(errEl, 'Network error. Please try again.');
  }
}

async function deleteSession(id) {
  try {
    const resp = await fetch(`/api/sessions/${id}`, { method: 'DELETE' });
    if (!resp.ok) {
      const errEl = document.getElementById('sessionError');
      showError(errEl, 'Failed to remove session. Please try again.');
      return;
    }
    await loadSessions();
  } catch (e) {
    const errEl = document.getElementById('sessionError');
    showError(errEl, 'Network error. Please try again.');
  }
}

// ---- HELPERS ----

function showError(el, msg) {
  el.textContent = msg;
  el.classList.remove('hidden');
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Allow pressing Enter in city/key inputs
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('cityInput').addEventListener('keydown', e => { if (e.key === 'Enter') fetchWeather(); });
  document.getElementById('apiKeyInput').addEventListener('keydown', e => { if (e.key === 'Enter') fetchWeather(); });
  loadSessions();
});
