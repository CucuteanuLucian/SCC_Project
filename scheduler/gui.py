"""
Graphical representation of the Gantt chart using only tkinter (standard library).
No third-party libraries needed.
"""

import tkinter as tk


COLORS = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
    "#59a14f", "#edc948", "#b07aa1", "#ff9da7",
    "#9c755f", "#bab0ac",
]
SYS_COLOR = "#d62728"
MEM_COLOR = "#aec7e8"
IDLE_COLOR = "#eeeeee"
ROW_HEIGHT = 40
TIME_SCALE = 20   # pixels per time unit
HEADER_H = 30
PADDING = 10


def show_gantt(event_log, processors_count):
    """Open a tkinter window with the Gantt chart."""
    end_time = 0
    for e in event_log:
        end_time = max(end_time, e.get("end_time", e.get("time", 0)))

    width = int(end_time * TIME_SCALE) + PADDING * 2 + 60
    height = processors_count * ROW_HEIGHT + HEADER_H + PADDING * 2

    root = tk.Tk()
    root.title("Process Scheduling Gantt Chart")

    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    # draw processor labels and idle background
    for i in range(processors_count):
        y = HEADER_H + i * ROW_HEIGHT
        canvas.create_text(PADDING, y + ROW_HEIGHT // 2,
                           text=f"P{i}", anchor="w", font=("Courier", 10, "bold"))
        canvas.create_rectangle(
            50, y, 50 + int(end_time * TIME_SCALE), y + ROW_HEIGHT,
            fill=IDLE_COLOR, outline="#cccccc"
        )

    # draw time axis
    step = max(1, int(end_time / 20))
    for t in range(0, int(end_time) + 1, step):
        x = 50 + int(t * TIME_SCALE)
        canvas.create_line(x, HEADER_H - 5, x, HEADER_H, fill="black")
        canvas.create_text(x, HEADER_H // 2, text=str(t), font=("Courier", 8))

    pid_color = {}
    color_idx = 0

    for e in event_log:
        etype = e.get("type")
        if etype not in ("RUN", "SYS_RUN", "SWAP_IN", "SWAP_OUT"):
            continue

        proc_id = e.get("processor", 0)
        t_start = e.get("time", 0)
        t_end = e.get("end_time", t_start)
        x0 = 50 + int(t_start * TIME_SCALE)
        x1 = 50 + int(t_end * TIME_SCALE)
        y0 = HEADER_H + proc_id * ROW_HEIGHT + 1
        y1 = HEADER_H + (proc_id + 1) * ROW_HEIGHT - 1

        if etype == "RUN":
            pid = e.get("pid")
            if pid not in pid_color:
                pid_color[pid] = COLORS[color_idx % len(COLORS)]
                color_idx += 1
            color = pid_color[pid]
            label = f"P{pid}"
        elif etype == "SYS_RUN":
            color = SYS_COLOR
            label = f"SYS({e.get('pid')})"
        else:
            color = MEM_COLOR
            label = "MEM"

        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#333333")
        if x1 - x0 > 15:
            canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2,
                               text=label, font=("Courier", 8), fill="white")

    root.mainloop()
