const GRID = {
  rows: 17,
  cols: 25,
  defaultStart: "8,5",
  defaultEnd: "8,19"
};

const ALGORITHM_LABELS = {
  greedy: "Voraz",
  astar: "A*"
};

const TOOL_LABELS = {
  start: "ubicar punto A",
  end: "ubicar punto B",
  wall: "poner obstáculos",
  erase: "borrar celdas"
};

const elements = {
  grid: document.getElementById("grid"),
  status: document.getElementById("status"),
  message: document.getElementById("message"),
  visitedStat: document.getElementById("visitedStat"),
  pathStat: document.getElementById("pathStat"),
  algorithmStat: document.getElementById("algorithmStat"),
  statsPanel: document.getElementById("statsPanel"),
  runBtn: document.getElementById("runBtn"),
  clearPathBtn: document.getElementById("clearPathBtn"),
  resetBtn: document.getElementById("resetBtn"),
  algorithmButtons: {
    greedy: document.getElementById("greedyBtn"),
    astar: document.getElementById("astarBtn")
  },
  toolButtons: {
    start: document.getElementById("startTool"),
    end: document.getElementById("endTool"),
    wall: document.getElementById("wallTool"),
    erase: document.getElementById("eraseTool")
  }
};

const state = {
  algorithm: "greedy",
  currentTool: "start",
  start: keyToCell(GRID.defaultStart),
  end: keyToCell(GRID.defaultEnd),
  walls: new Set(),
  visited: new Set(),
  path: new Set(),
  isPointerDown: false,
  isAnimating: false
};

function cellKey(row, col) {
  return `${row},${col}`;
}

function keyToCell(key) {
  const [row, col] = key.split(",").map(Number);
  return { row, col };
}

function sameCell(a, b) {
  return a.row === b.row && a.col === b.col;
}

function heuristic(a, b) {
  return Math.abs(a.row - b.row) + Math.abs(a.col - b.col);
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function renderGrid() {
  elements.grid.innerHTML = "";

  for (let row = 0; row < GRID.rows; row += 1) {
    for (let col = 0; col < GRID.cols; col += 1) {
      const button = createCellButton(row, col);
      elements.grid.appendChild(button);
    }
  }
}

function createCellButton(row, col) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = getCellClass(row, col);
  button.dataset.row = row;
  button.dataset.col = col;
  button.setAttribute("aria-label", `Fila ${row + 1}, columna ${col + 1}`);
  return button;
}

function getCellClass(row, col) {
  const key = cellKey(row, col);
  const cell = { row, col };
  const classes = ["cell"];

  if (sameCell(cell, state.start)) classes.push("start");
  else if (sameCell(cell, state.end)) classes.push("end");
  else if (state.walls.has(key)) classes.push("wall");
  else if (state.path.has(key)) classes.push("path");
  else if (state.visited.has(key)) classes.push("visited");

  return classes.join(" ");
}

function rerenderCell(row, col) {
  const index = row * GRID.cols + col;
  const cell = elements.grid.children[index];
  if (cell) {
    cell.className = getCellClass(row, col);
  }
}

function setAlgorithm(nextAlgorithm) {
  state.algorithm = nextAlgorithm;

  Object.entries(elements.algorithmButtons).forEach(([name, button]) => {
    button.classList.toggle("active", name === nextAlgorithm);
  });

  elements.algorithmStat.textContent = ALGORITHM_LABELS[nextAlgorithm];
  elements.statsPanel.dataset.algorithm = nextAlgorithm;
  document.body.dataset.algorithm = nextAlgorithm;
  clearPath();
}

function setTool(nextTool) {
  state.currentTool = nextTool;

  Object.entries(elements.toolButtons).forEach(([name, button]) => {
    button.classList.toggle("active", name === nextTool);
  });

  elements.status.textContent = `Modo: ${TOOL_LABELS[nextTool]}`;
}

function clearPath(render = true) {
  state.visited.clear();
  state.path.clear();
  elements.visitedStat.textContent = "0";
  elements.pathStat.textContent = "0";
  elements.message.textContent = "";
  if (render) renderGrid();
}

function clearPathBeforeEdit() {
  const hadSearchMarks = state.visited.size > 0 || state.path.size > 0;
  clearPath(hadSearchMarks);
  return hadSearchMarks;
}

function resetAll() {
  state.start = keyToCell(GRID.defaultStart);
  state.end = keyToCell(GRID.defaultEnd);
  state.walls.clear();
  clearPath();
  setTool("start");
}

function editCell(row, col) {
  if (state.isAnimating) return;

  const rendered = clearPathBeforeEdit();
  const key = cellKey(row, col);
  const cell = { row, col };

  if (state.currentTool === "start") {
    moveStart(cell, key, rendered);
    return;
  }

  if (state.currentTool === "end") {
    moveEnd(cell, key, rendered);
    return;
  }

  toggleWall(cell, key, rendered);
}

function moveStart(cell, key, rendered) {
  if (sameCell(cell, state.end)) return;

  const oldStart = { ...state.start };
  state.walls.delete(key);
  state.start = cell;
  refreshEditedCells(oldStart, cell, rendered);
}

function moveEnd(cell, key, rendered) {
  if (sameCell(cell, state.start)) return;

  const oldEnd = { ...state.end };
  state.walls.delete(key);
  state.end = cell;
  refreshEditedCells(oldEnd, cell, rendered);
}

function toggleWall(cell, key, rendered) {
  if (sameCell(cell, state.start) || sameCell(cell, state.end)) return;

  if (state.currentTool === "wall") {
    state.walls.add(key);
  } else if (state.currentTool === "erase") {
    state.walls.delete(key);
  }

  if (rendered) renderGrid();
  else rerenderCell(cell.row, cell.col);
}

function refreshEditedCells(previousCell, nextCell, rendered) {
  if (rendered) {
    renderGrid();
    return;
  }

  rerenderCell(previousCell.row, previousCell.col);
  rerenderCell(nextCell.row, nextCell.col);
}

function getNeighbors(cell) {
  const moves = [
    { row: cell.row - 1, col: cell.col },
    { row: cell.row + 1, col: cell.col },
    { row: cell.row, col: cell.col - 1 },
    { row: cell.row, col: cell.col + 1 }
  ];

  return moves.filter((next) => isWalkableCell(next));
}

function isWalkableCell(cell) {
  return cell.row >= 0 &&
    cell.row < GRID.rows &&
    cell.col >= 0 &&
    cell.col < GRID.cols &&
    !state.walls.has(cellKey(cell.row, cell.col));
}

function reconstructPath(cameFrom, endKey) {
  const route = [];
  let current = endKey;

  while (current) {
    route.unshift(current);
    current = cameFrom.get(current);
  }

  return route;
}

function searchRoute() {
  const startKey = cellKey(state.start.row, state.start.col);
  const endKey = cellKey(state.end.row, state.end.col);
  const open = [{ cell: state.start, key: startKey, g: 0, priority: 0 }];
  const closed = new Set();
  const cameFrom = new Map();
  const bestCost = new Map([[startKey, 0]]);
  const visitOrder = [];

  while (open.length > 0) {
    open.sort((a, b) => a.priority - b.priority || a.g - b.g);
    const current = open.shift();

    if (closed.has(current.key)) continue;
    closed.add(current.key);
    visitOrder.push(current.key);

    if (current.key === endKey) {
      return {
        found: true,
        visited: visitOrder,
        path: reconstructPath(cameFrom, endKey)
      };
    }

    addNeighborsToOpenList(current, open, closed, cameFrom, bestCost);
  }

  return { found: false, visited: visitOrder, path: [] };
}

function addNeighborsToOpenList(current, open, closed, cameFrom, bestCost) {
  for (const neighbor of getNeighbors(current.cell)) {
    const neighborKey = cellKey(neighbor.row, neighbor.col);
    if (closed.has(neighborKey)) continue;

    const nextG = current.g + 1;
    const knownG = bestCost.get(neighborKey);
    if (knownG !== undefined && nextG >= knownG) continue;

    cameFrom.set(neighborKey, current.key);
    bestCost.set(neighborKey, nextG);
    open.push(createOpenNode(neighbor, neighborKey, nextG));
  }
}

function createOpenNode(cell, key, g) {
  const h = heuristic(cell, state.end);
  const priority = state.algorithm === "astar" ? g + h : h;
  return { cell, key, g, priority };
}

async function runSearch() {
  if (state.isAnimating) return;

  clearPath();
  state.isAnimating = true;
  toggleButtons(true);
  elements.message.textContent = "Buscando ruta...";

  const result = searchRoute();
  await animateResult(result);
  showSearchResult(result);

  state.isAnimating = false;
  toggleButtons(false);
}

async function animateResult(result) {
  const startKey = cellKey(state.start.row, state.start.col);
  const endKey = cellKey(state.end.row, state.end.col);

  for (const key of result.visited) {
    if (key !== startKey && key !== endKey) {
      state.visited.add(key);
      updateAnimatedCell(key);
      await wait(10);
    }
  }

  for (const key of result.path) {
    if (key !== startKey && key !== endKey) {
      state.path.add(key);
      state.visited.delete(key);
      updateAnimatedCell(key);
      await wait(22);
    }
  }
}

function updateAnimatedCell(key) {
  const cell = keyToCell(key);
  rerenderCell(cell.row, cell.col);
}

function showSearchResult(result) {
  const steps = result.found ? Math.max(result.path.length - 1, 0) : 0;

  elements.visitedStat.textContent = String(result.visited.length);
  elements.pathStat.textContent = String(steps);
  elements.message.textContent = result.found
    ? `Ruta encontrada con ${algorithmDescription()} en ${steps} pasos.`
    : "No existe una ruta disponible con esos obstáculos.";
}

function algorithmDescription() {
  return state.algorithm === "greedy" ? "búsqueda voraz" : "A*";
}

function toggleButtons(disabled) {
  elements.runBtn.disabled = disabled;
  elements.clearPathBtn.disabled = disabled;
  elements.resetBtn.disabled = disabled;

  Object.values(elements.algorithmButtons).forEach((button) => {
    button.disabled = disabled;
  });

  Object.values(elements.toolButtons).forEach((button) => {
    button.disabled = disabled;
  });
}

function bindEvents() {
  elements.algorithmButtons.greedy.addEventListener("click", () => setAlgorithm("greedy"));
  elements.algorithmButtons.astar.addEventListener("click", () => setAlgorithm("astar"));

  Object.entries(elements.toolButtons).forEach(([tool, button]) => {
    button.addEventListener("click", () => setTool(tool));
  });

  elements.runBtn.addEventListener("click", runSearch);
  elements.clearPathBtn.addEventListener("click", () => clearPath());
  elements.resetBtn.addEventListener("click", resetAll);

  elements.grid.addEventListener("pointerdown", handleGridPointerDown);
  elements.grid.addEventListener("pointerover", handleGridPointerOver);
  window.addEventListener("pointermove", handleWindowPointerMove, { passive: false });
  window.addEventListener("pointerup", () => {
    state.isPointerDown = false;
  });
}

function handleGridPointerDown(event) {
  const cell = event.target.closest(".cell");
  if (!cell) return;

  state.isPointerDown = true;
  editCell(Number(cell.dataset.row), Number(cell.dataset.col));
}

function handleGridPointerOver(event) {
  if (!canPaintByDragging()) return;

  const cell = event.target.closest(".cell");
  if (!cell) return;

  editCell(Number(cell.dataset.row), Number(cell.dataset.col));
}

function handleWindowPointerMove(event) {
  if (!canPaintByDragging()) return;

  const target = document.elementFromPoint(event.clientX, event.clientY);
  const cell = target && target.closest(".cell");
  if (!cell || !elements.grid.contains(cell)) return;

  event.preventDefault();
  editCell(Number(cell.dataset.row), Number(cell.dataset.col));
}

function canPaintByDragging() {
  return state.isPointerDown && ["wall", "erase"].includes(state.currentTool);
}

function init() {
  bindEvents();
  renderGrid();
}

init();
