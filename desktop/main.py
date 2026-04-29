import tkinter as tk
from tkinter import ttk

from config import (
    ALGORITHMS,
    COLORS,
    COLS,
    DEFAULT_END,
    DEFAULT_START,
    ROWS,
    TOOL_MESSAGES,
    TOOLS,
)
from pathfinding import cell_key, key_to_cell, search_route


class GridPathfinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rutas en grilla - Voraz y A*")
        self.root.minsize(1000, 650)
        self.root.configure(bg=COLORS["background"])

        self.algorithm = tk.StringVar(value="greedy")
        self.current_tool = tk.StringVar(value="start")
        self.start = DEFAULT_START
        self.end = DEFAULT_END
        self.walls = set()
        self.visited = set()
        self.path = set()
        self.cells = {}
        self.is_animating = False
        self.is_dragging = False

        self.visited_stat = tk.StringVar(value="0")
        self.path_stat = tk.StringVar(value="0")
        self.algorithm_stat = tk.StringVar(value=ALGORITHMS["greedy"])
        self.status_text = tk.StringVar(value=TOOL_MESSAGES["start"])
        self.message_text = tk.StringVar(value="")

        self.configure_styles()
        self.build_layout()
        self.update_algorithm_theme()
        self.render_grid()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["background"])
        style.configure("Panel.TFrame", background=COLORS["panel"])
        style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"])
        style.configure("Panel.TLabel", background=COLORS["panel"], foreground=COLORS["text"])
        style.configure("Muted.TLabel", background=COLORS["panel"], foreground=COLORS["muted"])
        style.configure("Title.TLabel", background=COLORS["background"], foreground=COLORS["text"], font=("Arial", 24, "bold"))
        style.configure("Label.TLabel", background=COLORS["panel"], foreground="#3a4558", font=("Arial", 8, "bold"))
        style.configure("TButton", font=("Arial", 10), padding=8)
        style.configure("Primary.TButton", background=COLORS["accent"], foreground="#ffffff", font=("Arial", 10, "bold"))
        style.map("Primary.TButton", background=[("active", COLORS["accent_dark"])])

    def build_layout(self):
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 16))

        ttk.Label(header, text="Rutas en grilla", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Selecciona el punto A, el punto B, agrega obstaculos y compara busqueda voraz contra A*.",
            foreground=COLORS["muted"],
            background=COLORS["background"],
            font=("Arial", 10),
        ).pack(anchor="w", pady=(2, 0))

        workspace = ttk.Frame(container)
        workspace.pack(fill="both", expand=True)
        workspace.columnconfigure(1, weight=1)
        workspace.rowconfigure(0, weight=1)

        self.build_sidebar(workspace)
        self.build_board(workspace)

    def build_sidebar(self, parent):
        sidebar = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        self.add_algorithm_controls(sidebar)
        self.add_tool_controls(sidebar)
        self.add_action_controls(sidebar)
        self.add_stats(sidebar)
        self.add_legend(sidebar)

    def add_algorithm_controls(self, parent):
        group = ttk.Frame(parent, style="Panel.TFrame")
        group.pack(fill="x", pady=(0, 16))

        ttk.Label(group, text="ALGORITMO", style="Label.TLabel").pack(anchor="w", pady=(0, 8))
        for value, label in ALGORITHMS.items():
            ttk.Radiobutton(
                group,
                text=label,
                value=value,
                variable=self.algorithm,
                command=self.set_algorithm,
            ).pack(anchor="w", pady=2)

    def add_tool_controls(self, parent):
        group = ttk.Frame(parent, style="Panel.TFrame")
        group.pack(fill="x", pady=(0, 16))

        ttk.Label(group, text="EDITAR GRILLA", style="Label.TLabel").pack(anchor="w", pady=(0, 8))
        for value, label in TOOLS.items():
            ttk.Radiobutton(
                group,
                text=label,
                value=value,
                variable=self.current_tool,
                command=self.set_tool,
            ).pack(anchor="w", pady=2)

    def add_action_controls(self, parent):
        group = ttk.Frame(parent, style="Panel.TFrame")
        group.pack(fill="x", pady=(0, 16))

        ttk.Label(group, text="ACCIONES", style="Label.TLabel").pack(anchor="w", pady=(0, 8))
        self.run_button = ttk.Button(group, text="Buscar ruta", style="Primary.TButton", command=self.run_search)
        self.clear_button = ttk.Button(group, text="Limpiar recorrido", command=self.clear_path)
        self.reset_button = ttk.Button(group, text="Reiniciar todo", command=self.reset_all)

        self.run_button.pack(fill="x", pady=3)
        self.clear_button.pack(fill="x", pady=3)
        self.reset_button.pack(fill="x", pady=3)

    def add_stats(self, parent):
        group = ttk.Frame(parent, style="Panel.TFrame")
        group.pack(fill="x", pady=(0, 16))

        ttk.Label(group, text="RESULTADOS", style="Label.TLabel").pack(anchor="w", pady=(0, 8))
        self.stats_panel = tk.Frame(
            group,
            bg=COLORS["panel"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            padx=12,
            pady=12,
        )
        self.stats_panel.pack(fill="x")

        metrics_row = tk.Frame(self.stats_panel, bg=COLORS["panel"])
        metrics_row.pack(fill="x")
        metrics_row.columnconfigure(0, weight=1)
        metrics_row.columnconfigure(1, weight=1)

        self.visited_value_label = self.add_metric_card(metrics_row, "VISITADOS", self.visited_stat, 0)
        self.path_value_label = self.add_metric_card(metrics_row, "PASOS DE RUTA", self.path_stat, 1)

        self.algorithm_chip = tk.Frame(
            self.stats_panel,
            bg=COLORS["greedy_soft"],
            highlightbackground=COLORS["greedy"],
            highlightthickness=1,
            padx=10,
            pady=8,
        )
        self.algorithm_chip.pack(fill="x", pady=(10, 0))

        self.algorithm_chip_label = tk.Label(
            self.algorithm_chip,
            text="ALGORITMO",
            bg=COLORS["greedy_soft"],
            fg=COLORS["muted"],
            font=("Arial", 8, "bold"),
        )
        self.algorithm_chip_label.pack(side="left")
        self.algorithm_value_label = tk.Label(
            self.algorithm_chip,
            textvariable=self.algorithm_stat,
            bg=COLORS["greedy_soft"],
            fg=COLORS["greedy"],
            font=("Arial", 10, "bold"),
        )
        self.algorithm_value_label.pack(side="right")

    def add_metric_card(self, parent, label, value, column):
        card = tk.Frame(
            parent,
            bg=COLORS["metric_bg"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            padx=10,
            pady=10,
        )
        card.grid(row=0, column=column, sticky="ew", padx=(0, 6) if column == 0 else (6, 0))

        tk.Label(
            card,
            text=label,
            bg=COLORS["metric_bg"],
            fg=COLORS["muted"],
            font=("Arial", 8, "bold"),
        ).pack(anchor="w")
        value_label = tk.Label(
            card,
            textvariable=value,
            bg=COLORS["metric_bg"],
            fg=COLORS["text"],
            font=("Arial", 20, "bold"),
        )
        value_label.pack(anchor="w", pady=(6, 0))
        return value_label

    def add_legend(self, parent):
        group = ttk.Frame(parent, style="Panel.TFrame")
        group.pack(fill="x")

        ttk.Label(group, text="LEYENDA", style="Label.TLabel").pack(anchor="w", pady=(0, 8))
        for label, color in [
            ("A", COLORS["start"]),
            ("B", COLORS["end"]),
            ("Obstaculo", COLORS["wall"]),
            ("Ruta", COLORS["path"]),
            ("Visitado", COLORS["visited"]),
        ]:
            row = ttk.Frame(group, style="Panel.TFrame")
            row.pack(fill="x", pady=2)
            swatch = tk.Frame(row, width=16, height=16, bg=color, highlightbackground=COLORS["line"], highlightthickness=1)
            swatch.pack(side="left", padx=(0, 8))
            ttk.Label(row, text=label, style="Muted.TLabel").pack(side="left")

    def build_board(self, parent):
        board = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        board.grid(row=0, column=1, sticky="nsew")
        board.columnconfigure(0, weight=1)
        board.rowconfigure(1, weight=1)

        top = ttk.Frame(board, style="Panel.TFrame")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(top, textvariable=self.status_text, style="Panel.TLabel", font=("Arial", 10, "bold")).pack(side="left")
        ttk.Label(
            top,
            text="Arrastra sobre la grilla para dibujar o borrar obstaculos.",
            style="Muted.TLabel",
        ).pack(side="right")

        self.grid_frame = tk.Frame(board, bg=COLORS["line"], highlightbackground=COLORS["line"], highlightthickness=1)
        self.grid_frame.grid(row=1, column=0, sticky="nsew")

        for row in range(ROWS):
            self.grid_frame.rowconfigure(row, weight=1, uniform="grid_row")
        for col in range(COLS):
            self.grid_frame.columnconfigure(col, weight=1, uniform="grid_col")

        ttk.Label(board, textvariable=self.message_text, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(12, 0))

    def render_grid(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.create_or_update_cell(row, col)

    def create_or_update_cell(self, row, col):
        key = cell_key(row, col)
        cell = self.cells.get(key)

        if cell is None:
            cell = tk.Label(
                self.grid_frame,
                text="",
                bg=COLORS["cell"],
                relief="solid",
                bd=1,
                font=("Arial", 9, "bold"),
                width=2,
                height=1,
            )
            cell.grid(row=row, column=col, sticky="nsew")
            cell.bind("<Button-1>", lambda event, r=row, c=col: self.handle_cell_click(r, c))
            cell.bind("<B1-Motion>", lambda event: self.handle_drag(event))
            cell.bind("<ButtonRelease-1>", lambda event: self.stop_dragging())
            self.cells[key] = cell

        self.style_cell(row, col)

    def style_cell(self, row, col):
        key = cell_key(row, col)
        cell = self.cells[key]
        text = ""
        color = COLORS["cell"]
        foreground = COLORS["text"]

        if (row, col) == self.start:
            text = "A"
            color = COLORS["start"]
            foreground = "#ffffff"
        elif (row, col) == self.end:
            text = "B"
            color = COLORS["end"]
            foreground = "#ffffff"
        elif key in self.walls:
            color = COLORS["wall"]
            foreground = "#ffffff"
        elif key in self.path:
            color = COLORS["path"]
        elif key in self.visited:
            color = COLORS["visited"]

        cell.configure(text=text, bg=color, fg=foreground)

    def rerender_cell(self, cell):
        self.style_cell(*cell)

    def set_algorithm(self):
        self.algorithm_stat.set(ALGORITHMS[self.algorithm.get()])
        self.update_algorithm_theme()
        self.clear_path()

    def update_algorithm_theme(self):
        algorithm = self.algorithm.get()
        accent = COLORS["astar"] if algorithm == "astar" else COLORS["greedy"]
        surface = COLORS["astar_soft"] if algorithm == "astar" else COLORS["greedy_soft"]

        self.visited_value_label.configure(fg=accent)
        self.algorithm_chip.configure(bg=surface, highlightbackground=accent)
        self.algorithm_chip_label.configure(bg=surface)
        self.algorithm_value_label.configure(bg=surface, fg=accent)

        style = ttk.Style()
        style.configure("Primary.TButton", background=accent, foreground="#ffffff", font=("Arial", 10, "bold"))
        style.map("Primary.TButton", background=[("active", accent)])

    def set_tool(self):
        self.status_text.set(TOOL_MESSAGES[self.current_tool.get()])

    def clear_path(self, render=True):
        self.visited.clear()
        self.path.clear()
        self.visited_stat.set("0")
        self.path_stat.set("0")
        self.message_text.set("")

        if render:
            self.render_grid()

    def clear_path_before_edit(self):
        had_marks = bool(self.visited or self.path)
        self.clear_path(render=had_marks)
        return had_marks

    def reset_all(self):
        if self.is_animating:
            return

        self.start = DEFAULT_START
        self.end = DEFAULT_END
        self.walls.clear()
        self.current_tool.set("start")
        self.set_tool()
        self.clear_path()

    def handle_cell_click(self, row, col):
        self.is_dragging = True
        self.edit_cell(row, col)

    def handle_drag(self, event):
        if not self.is_dragging or self.current_tool.get() not in ("wall", "erase"):
            return

        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if widget is None:
            return

        for key, cell in self.cells.items():
            if cell == widget:
                row, col = key_to_cell(key)
                self.edit_cell(row, col)
                break

    def stop_dragging(self):
        self.is_dragging = False

    def edit_cell(self, row, col):
        if self.is_animating:
            return

        rendered = self.clear_path_before_edit()
        key = cell_key(row, col)
        selected = (row, col)
        tool = self.current_tool.get()

        if tool == "start":
            self.move_start(selected, key, rendered)
        elif tool == "end":
            self.move_end(selected, key, rendered)
        else:
            self.toggle_wall(selected, key, rendered)

    def move_start(self, selected, key, rendered):
        if selected == self.end:
            return

        previous = self.start
        self.walls.discard(key)
        self.start = selected
        self.refresh_edited_cells(previous, selected, rendered)

    def move_end(self, selected, key, rendered):
        if selected == self.start:
            return

        previous = self.end
        self.walls.discard(key)
        self.end = selected
        self.refresh_edited_cells(previous, selected, rendered)

    def toggle_wall(self, selected, key, rendered):
        if selected in (self.start, self.end):
            return

        if self.current_tool.get() == "wall":
            self.walls.add(key)
        elif self.current_tool.get() == "erase":
            self.walls.discard(key)

        if rendered:
            self.render_grid()
        else:
            self.rerender_cell(selected)

    def refresh_edited_cells(self, previous, selected, rendered):
        if rendered:
            self.render_grid()
            return

        self.rerender_cell(previous)
        self.rerender_cell(selected)

    def run_search(self):
        if self.is_animating:
            return

        self.clear_path()
        self.is_animating = True
        self.toggle_controls("disabled")
        self.message_text.set("Buscando ruta...")

        result = search_route(self.start, self.end, self.walls, self.algorithm.get())
        self.animate_visited(result, 0)

    def animate_visited(self, result, index):
        if index >= len(result["visited"]):
            self.animate_path(result, 0)
            return

        key = result["visited"][index]
        if key not in (cell_key(*self.start), cell_key(*self.end)):
            self.visited.add(key)
            self.rerender_cell(key_to_cell(key))

        self.root.after(10, lambda: self.animate_visited(result, index + 1))

    def animate_path(self, result, index):
        if index >= len(result["path"]):
            self.show_search_result(result)
            self.is_animating = False
            self.toggle_controls("normal")
            return

        key = result["path"][index]
        if key not in (cell_key(*self.start), cell_key(*self.end)):
            self.path.add(key)
            self.visited.discard(key)
            self.rerender_cell(key_to_cell(key))

        self.root.after(22, lambda: self.animate_path(result, index + 1))

    def show_search_result(self, result):
        steps = max(len(result["path"]) - 1, 0) if result["found"] else 0
        algorithm_text = "busqueda voraz" if self.algorithm.get() == "greedy" else "A*"

        self.visited_stat.set(str(len(result["visited"])))
        self.path_stat.set(str(steps))

        if result["found"]:
            self.message_text.set(f"Ruta encontrada con {algorithm_text} en {steps} pasos.")
        else:
            self.message_text.set("No existe una ruta disponible con esos obstaculos.")

    def toggle_controls(self, state):
        self.run_button.configure(state=state)
        self.clear_button.configure(state=state)
        self.reset_button.configure(state=state)


def main():
    root = tk.Tk()
    app = GridPathfinderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
