import { validateDraft } from "./validator.js";

const field = id => document.getElementById(id);
const pool = field("pool");
const status = field("status");
const offlineBuild = field("offline-build");
const mode = field("mode");
const action = field("action");
const advance = field("advance");
const importFile = field("import");
const exportFile = field("export");
const limit = { blue: 5, red: 5, bans: 10 };
const stateLabels = { fearless_locked: "Locked", picked: "Picked", banned: "Banned", available: "Available", unavailable: "Unavailable" };
const boardStates = ["fearless_locked", "picked", "banned", "available"];
const maxSeriesBytes = 64_000;
const sizeError = "Choose a series JSON file under 64 KB.";
let current;
let busy = false;

function makeButton(text, handler) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = text;
  if (handler) button.addEventListener("click", handler);
  return button;
}

function render() {
  const { board, draft } = current;
  offlineBuild.hidden = true;
  field("series").textContent = board.complete ? "Five games recorded" : `Game ${board.game} · ${draft.history.length} recorded`;
  mode.value = board.mode;
  mode.disabled = busy;
  action.disabled = busy || board.complete;
  advance.disabled = busy || board.complete || draft.blue.length !== 5 || draft.red.length !== 5;
  exportFile.disabled = importFile.disabled = busy;
  field("history").replaceChildren(...draft.history.map(game => {
    const item = document.createElement("li");
    item.textContent = `Blue: ${game.blue.join(", ")} · Red: ${game.red.join(", ")}`;
    return item;
  }));
  for (const lane of ["blue", "red", "bans"]) {
    const rows = draft[lane].map((champion, index) => {
      const item = document.createElement("li");
      const remove = makeButton(`Remove ${champion}`, () => update(next => next[lane].splice(index, 1)));
      remove.disabled = busy;
      item.append(remove);
      return item;
    });
    field(lane).replaceChildren(...rows);
  }
  field("counts").textContent = `${board.available.length} available · ${board.fearless_locked.length} locked by prior games`;
  /** @type {Map<string, string>} */
  const states = new Map();
  for (const key of boardStates) {
    for (const champion of board[key]) states.set(champion, key);
  }
  pool.replaceChildren(...draft.pool.map(champion => {
    const state = states.get(champion) ?? "unavailable";
    const button = makeButton(`${champion} · ${stateLabels[state]}`, () => {
      const lane = action.value;
      if (draft[lane].length >= limit[lane]) {
        status.textContent = "That group is full. Remove a champion or select another group.";
        return;
      }
      void update(next => next[lane].push(champion), `Added ${champion}.`);
    });
    button.dataset.state = state;
    button.disabled = busy || board.complete || state !== "available";
    return button;
  }));
}

async function acceptDraft(load, message = "") {
  if (busy) return;
  busy = true;
  mode.disabled = action.disabled = advance.disabled = true;
  exportFile.disabled = importFile.disabled = true;
  for (const button of document.querySelectorAll(".slots button, #pool button")) button.disabled = true;
  try {
    const next = await load();
    const board = await validateDraft(next);
    const draft = {
      mode: board.mode, pool: next.pool, history: next.history ?? [],
      blue: board.blue, red: board.red, bans: board.banned,
    };
    if (new Blob([JSON.stringify(draft)]).size > maxSeriesBytes) throw new Error(sizeError);
    current = { draft, board };
    status.textContent = message;
  } catch (error) {
    status.textContent = error.message;
  } finally {
    busy = false;
    importFile.disabled = false;
    if (current) render();
  }
}

function update(change, message) {
  return acceptDraft(() => {
    const next = structuredClone(current.draft);
    change(next);
    return next;
  }, message);
}

mode.disabled = action.disabled = true;
mode.addEventListener("change", () => update(draft => { draft.mode = mode.value; }, "Draft rules updated."));
advance.addEventListener("click", () => update(draft => {
  draft.history.push({ blue: draft.blue, red: draft.red });
  draft.blue = [];
  draft.red = [];
  draft.bans = [];
}, "Recorded the game and cleared its bans."));
importFile.addEventListener("change", () => {
  const [file] = importFile.files;
  if (!file) return;
  importFile.value = "";
  void acceptDraft(async () => {
    if (file.size > maxSeriesBytes) throw new Error(sizeError);
    return JSON.parse(await file.text());
  }, "Series imported.");
});
exportFile.addEventListener("click", () => {
  const options = { type: "application/json" };
  let blob = new Blob([JSON.stringify(current.draft, null, 2)], options);
  if (blob.size > maxSeriesBytes) {
    blob = new Blob([JSON.stringify(current.draft)], options);
  }
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "draft-desk-series.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
});

async function loadSeries() {
  const fixture = await fetch("./demo.json");
  if (!fixture.ok) throw new Error("Unable to load the synthetic series.");
  return fixture.json();
}

await acceptDraft(loadSeries, "Synthetic series loaded.");
if (!current && document.querySelector('meta[name="draft-validator"]').content === "browser") {
  field("series").textContent = "Browser demo unavailable";
  status.textContent = "The browser demo could not start. Reload the page or use the offline build.";
  offlineBuild.hidden = false;
}
