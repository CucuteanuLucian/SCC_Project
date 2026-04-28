"""
Input parser: reads simulation parameters and process definitions from a text file.

Expected file format
--------------------
PROCESSORS <n>
MEMORY <ram>
TIME_SLICE <q>
SYSCALL_PERIOD <p>
DISK_TRANSFER_RATE <r>

PROCESS <pid> <release_time> <memory>
BURSTS <n> <b0> [<s0> <b1> <s1> ... <bn-1>]
...

Lines starting with '#' are treated as comments and ignored.
Blank lines are ignored.
"""

from models import Process


def parse_file(path):
    """
    Parse the simulation input file.

    Returns
    -------
    params   : dict with keys processors, memory, time_slice,
                             syscall_period, disk_transfer_rate
    processes: list of Process objects
    """
    params = {}
    processes = []

    with open(path, "r") as fh:
        lines = fh.readlines()

    i = 0
    current_process = None

    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if not line or line.startswith("#"):
            continue

        tokens = line.split()
        keyword = tokens[0].upper()

        if keyword == "PROCESSORS":
            params["processors"] = int(tokens[1])

        elif keyword == "MEMORY":
            params["memory"] = float(tokens[1])

        elif keyword == "TIME_SLICE":
            params["time_slice"] = float(tokens[1])

        elif keyword == "SYSCALL_PERIOD":
            params["syscall_period"] = float(tokens[1])

        elif keyword == "DISK_TRANSFER_RATE":
            params["disk_transfer_rate"] = float(tokens[1])

        elif keyword == "PROCESS":
            # PROCESS <pid> <release_time> <memory>
            pid = int(tokens[1])
            release_time = float(tokens[2])
            memory = float(tokens[3])
            current_process = {"pid": pid, "release_time": release_time,
                               "memory": memory, "bursts": [], "syscalls": []}
            processes.append(current_process)

        elif keyword == "BURSTS":
            # BURSTS <count> b0 [s0 b1 s1 ... b_count-1]
            assert current_process is not None, "BURSTS line without preceding PROCESS"
            count = int(tokens[1])
            values = [float(x) for x in tokens[2:]]
            # interleaved: b s b s ... b  => count bursts, count-1 syscalls
            bursts = []
            syscalls = []
            for j in range(count):
                bursts.append(values[j * 2])
                if j < count - 1:
                    syscalls.append(values[j * 2 + 1])
            current_process["bursts"] = bursts
            current_process["syscalls"] = syscalls

    # build Process objects
    proc_objects = []
    for p in processes:
        proc_objects.append(
            Process(p["pid"], p["release_time"], p["memory"],
                    p["bursts"], p["syscalls"])
        )

    _validate_params(params)
    return params, proc_objects


def _validate_params(params):
    required = ["processors", "memory", "time_slice", "syscall_period",
                "disk_transfer_rate"]
    for key in required:
        assert key in params, f"Missing simulation parameter: {key}"
    assert params["processors"] >= 1
    assert params["memory"] > 0
    assert params["time_slice"] > 0
    assert params["syscall_period"] > 0
    assert params["disk_transfer_rate"] > 0
