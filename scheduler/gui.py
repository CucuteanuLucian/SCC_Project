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
    """Open a scrollable tkinter window with the Gantt chart."""
    end_time = 0
    for e in event_log:
        end_time = max(end_time, e.get("end_time", e.get("time", 0)))

    # full canvas dimensions (may be larger than the screen)
    canvas_w = int(end_time * TIME_SCALE) + PADDING * 2 + 60
    # add one extra row for system/memory/instant events
    canvas_h = (processors_count + 1) * ROW_HEIGHT + HEADER_H + PADDING * 2

    # window size capped to 90% of screen
    root = tk.Tk()
    root.title("Process Scheduling Gantt Chart")
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    win_w = min(canvas_w + 20, int(screen_w * 0.9))
    win_h = min(canvas_h + 20, int(screen_h * 0.9))
    root.geometry(f"{win_w}x{win_h}")

    # scrollbars
    h_scroll = tk.Scrollbar(root, orient=tk.HORIZONTAL)
    v_scroll = tk.Scrollbar(root, orient=tk.VERTICAL)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(
        root, bg="white",
        scrollregion=(0, 0, canvas_w, canvas_h),
        xscrollcommand=h_scroll.set,
        yscrollcommand=v_scroll.set,
    )
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    h_scroll.config(command=canvas.xview)
    v_scroll.config(command=canvas.yview)

    # mouse-wheel scroll (horizontal on most Gantt charts)
    def _on_mousewheel(event):
        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    root.bind("<MouseWheel>", _on_mousewheel)
    root.bind("<Shift-MouseWheel>", _on_shift_mousewheel)
    # Linux scroll events
    root.bind("<Button-4>", lambda e: canvas.xview_scroll(-1, "units"))
    root.bind("<Button-5>", lambda e: canvas.xview_scroll(1, "units"))

    # draw top row for system/memory/instant events
    top_y = HEADER_H - ROW_HEIGHT
    canvas.create_text(PADDING, top_y + ROW_HEIGHT // 2,
                       text="SYS/MEM", anchor="w", font=("Courier", 10, "bold"))
    canvas.create_rectangle(
        50, top_y, 50 + int(end_time * TIME_SCALE), top_y + ROW_HEIGHT,
        fill=IDLE_COLOR, outline="#cccccc"
    )

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

    # helper for tooltips (floating window, not on canvas)
    tooltip_window = {"win": None}

    def _show_tooltip(ev, text):
        # remove existing tooltip
        if tooltip_window["win"]:
            tooltip_window["win"].destroy()
            tooltip_window["win"] = None
        
        # create a floating toplevel window
        tw = tk.Toplevel(root)
        tw.wm_overrideredirect(True)
        
        # create label with text
        label = tk.Label(tw, text=text, background="#ffffe0", relief=tk.SOLID, 
                        borderwidth=1, font=("Courier", 8), justify=tk.LEFT)
        label.pack()
        
        # position window near mouse in window coordinates
        x = root.winfo_x() + ev.x + 15
        y = root.winfo_y() + ev.y + 15
        
        # clamp to screen to keep visible
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        req_w = label.winfo_reqwidth()
        req_h = label.winfo_reqheight()
        
        if x + req_w > screen_w:
            x = max(0, root.winfo_x() + ev.x - req_w - 5)
        if y + req_h > screen_h:
            y = max(0, root.winfo_y() + ev.y - req_h - 5)
        
        tw.wm_geometry(f"+{x}+{y}")
        tooltip_window["win"] = tw

    def _hide_tooltip(ev=None):
        if tooltip_window["win"]:
            tooltip_window["win"].destroy()
            tooltip_window["win"] = None

    for idx, e in enumerate(event_log):
        etype = e.get("type")
        # draw all event types; position by processor if present, else top row
        proc_field = e.get("processor")
        if proc_field is None:
            proc_row = -1
        else:
            proc_row = int(proc_field)

        t_start = e.get("time", 0)
        t_end = e.get("end_time", t_start)
        x0 = 50 + int(t_start * TIME_SCALE)
        x1 = 50 + int(t_end * TIME_SCALE)

        if proc_row >= 0:
            y0 = HEADER_H + proc_row * ROW_HEIGHT + 1
            y1 = HEADER_H + (proc_row + 1) * ROW_HEIGHT - 1
        else:
            y0 = HEADER_H - ROW_HEIGHT + 1
            y1 = HEADER_H - 1

        label = e.get("type")
        color = MEM_COLOR

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
        elif etype in ("SWAP_IN", "SWAP_OUT"):
            color = MEM_COLOR
            label = "MEM"
        elif etype in ("RELEASE", "MEM_READY", "SYSCALL_QUEUED", "SYSCALL_DONE", "DONE", "SYS_RELEASE", "SIMULATION_END"):
            color = "#ffffff"

        # draw zero-duration events as vertical lines
        if x1 <= x0 + 2:
            line_id = canvas.create_line(x0, y0, x0, y1, fill="#333333")
            text_id = canvas.create_text(x0 + 3, y0 - 6, text=label, anchor="w", font=("Courier", 7))
            tag = f"evt_{idx}"
            canvas.addtag_withtag(tag, line_id)
            canvas.addtag_withtag(tag, text_id)
            formatted = "\n".join(f"{k}: {v}" for k, v in e.items())
            canvas.tag_bind(tag, "<Enter>", lambda ev, txt=formatted: _show_tooltip(ev, txt))
            canvas.tag_bind(tag, "<Leave>", lambda ev: _hide_tooltip(ev))
        else:
            rect_id = canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#333333")
            if x1 - x0 > 15:
                canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2,
                                   text=label, font=("Courier", 8), fill="white")
            tag = f"evt_{idx}"
            canvas.addtag_withtag(tag, rect_id)
            formatted = "\n".join(f"{k}: {v}" for k, v in e.items())
            canvas.tag_bind(tag, "<Enter>", lambda ev, txt=formatted: _show_tooltip(ev, txt))
            canvas.tag_bind(tag, "<Leave>", lambda ev: _hide_tooltip(ev))

    root.mainloop()
