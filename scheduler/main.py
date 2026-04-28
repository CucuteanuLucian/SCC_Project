"""
Main entry point.

Usage:
    python main.py <input_file> [--no-gui]

Outputs:
    report.txt   - text event log
    gantt.txt    - ASCII Gantt chart
    (optional)   - graphical Gantt chart window
"""

import sys

from parser import parse_file
from simulator import Simulator
from output import write_text_report, write_gantt


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [--no-gui]")
        sys.exit(1)

    input_file = sys.argv[1]
    show_gui = "--no-gui" not in sys.argv

    print(f"[*] Parsing input: {input_file}")
    params, processes = parse_file(input_file)

    print(f"[*] Processors : {params['processors']}")
    print(f"[*] RAM        : {params['memory']}")
    print(f"[*] Time slice : {params['time_slice']}")
    print(f"[*] Sys period : {params['syscall_period']}")
    print(f"[*] Disk rate  : {params['disk_transfer_rate']}")
    print(f"[*] Processes  : {len(processes)}")

    sim = Simulator(params, processes)
    print("[*] Running simulation...")
    event_log = sim.run()

    write_text_report(event_log, "report.txt")
    print("[*] Text report written to report.txt")

    write_gantt(event_log, params["processors"], "gantt.txt")
    print("[*] ASCII Gantt chart written to gantt.txt")

    if show_gui:
        print("[*] Opening graphical Gantt chart...")
        from gui import show_gantt
        show_gantt(event_log, params["processors"])


if __name__ == "__main__":
    main()
