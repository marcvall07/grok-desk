// app.js — Plan B poller + tab navigation + screens
const DATA_PATH = new URLSearchParams(location.hash.slice(1)).get("d") || localStorage.getItem("data_path") || "mxyBeeDto79uuE75jmEgAl74p8XYZbPK89u4FgO_nsc";
if (DATA_PATH) localStorage.setItem("data_path", DATA_PATH);

const screens = document.querySelectorAll(".screen");
const tabs = document.querySelectorAll(".tabbar button");

function show(screen) {
  screens.forEach(s => s.classList.remove("active"));
  document.getElementById(screen).classList.add("active");
  tabs.forEach(t => t.classList.toggle("active", t.dataset.screen === screen));
}

tabs.forEach(btn => {
  btn.addEventListener("click", () => show(btn.dataset.screen));
});

async function loadJSON(name) {
  const r = await fetch(`/d/${DATA_PATH}/${name}.json?t=${Date.now()}`);
  if (!r.ok) return null;
  return r.json();
}

async function refresh() {
  const state = await loadJSON("state");
  const activity = await loadJSON("activity") || { rows: [] };

  if (state) {
    document.getElementById("balance").textContent = `$${Number(state.balance).toFixed(2)}`;
    document.getElementById("today").textContent = `${state.today_pct >= 0 ? "+" : ""}${Number(state.today_pct).toFixed(2)}%`;
    document.getElementById("multiplier").textContent = `${Number(state.multiplier).toFixed(2)}×`;
    document.getElementById("mode-display").textContent = state.mode;
    document.getElementById("stack-display").textContent = `$${Number(state.balance).toFixed(0)}`;
    const stop = state.settings?.stop_pct || 6;
    document.getElementById("stop-display").textContent = `-${stop}%`;
    const badge = document.querySelector(".paper-badge");
    if (badge) badge.style.display = state.mode === "PAPER" ? "inline" : "none";
  }

  // Home activity (last 5)
  const homeAct = document.getElementById("home-activity");
  homeAct.innerHTML = activity.rows.slice(0, 5).map(r => `
    <div class="activity-row">
      <div>${r.title}<div class="sub">${r.subtitle}</div></div>
      <div>${r.value}</div>
    </div>
  `).join("") || `<div class="chart-placeholder">Nothing yet tonight</div>`;

  // Full activity
  document.getElementById("activity-list").innerHTML = activity.rows.map(r => `
    <div class="activity-row">
      <div>${r.title}<div class="sub">${r.subtitle}</div></div>
      <div>${r.value}</div>
    </div>
  `).join("") || `<div class="chart-placeholder">Nothing yet tonight</div>`;

  // Agents list
  const agents = [
    { name: "Scanner", color: "#64d2ff", status: state?.agents_status?.scanner || "running" },
    { name: "Auditor", color: "#fff", status: state?.agents_status?.auditor || "running" },
    { name: "Analyst", color: "#ffd60a", status: state?.agents_status?.analyst || "running" },
    { name: "Executor", color: "#00d35a", status: state?.agents_status?.executor || "running" },
    { name: "Risk", color: "#ff6b9a", status: state?.agents_status?.risk || "running" },
  ];
  document.getElementById("agents-list").innerHTML = agents.map(a => `
    <div class="row">
      <span style="color:${a.color}">${a.name}</span>
      <span>${a.status}</span>
    </div>
  `).join("");

  // Agent carousel on home
  document.getElementById("agent-carousel").innerHTML = agents.map(a => `
    <div class="agent-card">
      <div style="color:${a.color};font-weight:600">${a.name}</div>
      <div style="color:var(--secondary);margin-top:8px">${a.status}</div>
    </div>
  `).join("");
}

setInterval(refresh, 15000);
refresh();
show("home");
