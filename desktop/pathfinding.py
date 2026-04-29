from config import COLS, ROWS


def cell_key(row, col):
    return f"{row},{col}"


def key_to_cell(key):
    row, col = key.split(",")
    return int(row), int(col)


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(cell, walls):
    row, col = cell
    moves = [
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]

    return [
        move for move in moves
        if is_walkable(move, walls)
    ]


def is_walkable(cell, walls):
    row, col = cell
    return (
        0 <= row < ROWS and
        0 <= col < COLS and
        cell_key(row, col) not in walls
    )


def reconstruct_path(came_from, end_key):
    route = []
    current = end_key

    while current:
        route.insert(0, current)
        current = came_from.get(current)

    return route


def search_route(start, end, walls, algorithm):
    start_key = cell_key(*start)
    end_key = cell_key(*end)
    open_list = [{"cell": start, "key": start_key, "g": 0, "priority": 0}]
    closed = set()
    came_from = {}
    best_cost = {start_key: 0}
    visit_order = []

    while open_list:
        open_list.sort(key=lambda node: (node["priority"], node["g"]))
        current = open_list.pop(0)

        if current["key"] in closed:
            continue

        closed.add(current["key"])
        visit_order.append(current["key"])

        if current["key"] == end_key:
            return {
                "found": True,
                "visited": visit_order,
                "path": reconstruct_path(came_from, end_key),
            }

        for neighbor in get_neighbors(current["cell"], walls):
            neighbor_key = cell_key(*neighbor)
            if neighbor_key in closed:
                continue

            next_g = current["g"] + 1
            known_g = best_cost.get(neighbor_key)
            if known_g is not None and next_g >= known_g:
                continue

            came_from[neighbor_key] = current["key"]
            best_cost[neighbor_key] = next_g
            open_list.append(create_open_node(neighbor, neighbor_key, next_g, end, algorithm))

    return {"found": False, "visited": visit_order, "path": []}


def create_open_node(cell, key, g, end, algorithm):
    h = heuristic(cell, end)
    priority = g + h if algorithm == "astar" else h
    return {"cell": cell, "key": key, "g": g, "priority": priority}
