"""
Output module: text report and ASCII Gantt chart.
No third-party libraries used.
"""


def write_text_report(event_log, path):
    """Write a human-readable text log of all events."""
    with open(path, "w") as fh:
        fh.write(f"{'TIME':>10}  {'END_TIME':>10}  {'TYPE':<20}  DETAILS\n")
        fh.write("-" * 70 + "\n")
        for e in event_log:
            t = e.get("time", "")
            end = e.get("end_time", e.get("time", ""))
            etype = e.get("type", "")
            details = {k: v for k, v in e.items()
                       if k not in ("time", "end_time", "type")}
            fh.write(f"{t:>10.2f}  {end:>10.2f}  {etype:<20}  {details}\n")


def write_gantt(event_log, processors_count, path):
    """
    Write a simple ASCII Gantt chart.
    Each row is a processor; columns are integer time units.
    """
    # determine simulation end time
    end_time = 0
    for e in event_log:
        end_time = max(end_time, e.get("end_time", e.get("time", 0)))

    end_time = int(end_time) + 1
    # grid[processor][t] = label character
    grid = [["." for _ in range(end_time)] for _ in range(processors_count)]

    for e in event_log:
        etype = e.get("type")
        if etype in ("RUN", "SYS_RUN", "SWAP_IN", "SWAP_OUT"):
            proc_id = e.get("processor", 0)
            t_start = int(e.get("time", 0))
            t_end = int(e.get("end_time", t_start))
            if etype == "RUN":
                label = str(e.get("pid", "?"))[0]
            elif etype == "SYS_RUN":
                label = "S"
            else:
                label = "M"   # memory transfer
            for t in range(t_start, min(t_end, end_time)):
                grid[proc_id][t] = label

    with open(path, "w") as fh:
        # header
        header_step = 10
        fh.write("CPU  ")
        for t in range(0, end_time, header_step):
            fh.write(f"{t:<{header_step}}")
        fh.write("\n")
        fh.write("     " + "-" * end_time + "\n")
        for pid, row in enumerate(grid):
            fh.write(f"P{pid:<3} |{''.join(row)}|\n")
        fh.write("\nLegend: digit=process id  S=system call  M=memory transfer  .=idle\n")
