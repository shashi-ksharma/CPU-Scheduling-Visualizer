
def calculate_metrics(processes, completion):
    results = []
    total_waiting = 0
    total_turnaround = 0

    for p in processes:
        pid = p["pid"]
        turnaround = completion[pid] - p["arrival"]
        waiting = turnaround - p["burst"]

        results.append({
            "pid": pid,
            "waiting": waiting,
            "turnaround": turnaround
        })

        total_waiting += waiting
        total_turnaround += turnaround

    count = len(processes)

    return results, total_waiting / count, total_turnaround / count


def fcfs(processes):
    procs = sorted(processes, key=lambda p: (p["arrival"], p["pid"]))
    time = 0
    completion = {}
    gantt = []

    for p in procs:
        if time < p["arrival"]:
            gantt.append(("Idle", time, p["arrival"]))
            time = p["arrival"]

        start = time
        time += p["burst"]
        completion[p["pid"]] = time
        gantt.append((p["pid"], start, time))

    return calculate_metrics(processes, completion) + (gantt,)


def sjf(processes):
    remaining = processes.copy()
    time = 0
    completion = {}
    gantt = []

    while remaining:
        available = [p for p in remaining if p["arrival"] <= time]

        if not available:
            next_arrival = min(p["arrival"] for p in remaining)
            gantt.append(("Idle", time, next_arrival))
            time = next_arrival
            continue

        p = min(available, key=lambda x: (x["burst"], x["arrival"], x["pid"]))
        start = time
        time += p["burst"]
        completion[p["pid"]] = time
        gantt.append((p["pid"], start, time))
        remaining.remove(p)

    return calculate_metrics(processes, completion) + (gantt,)


def priority_scheduling(processes):
    remaining = processes.copy()
    time = 0
    completion = {}
    gantt = []

    while remaining:
        available = [p for p in remaining if p["arrival"] <= time]

        if not available:
            next_arrival = min(p["arrival"] for p in remaining)
            gantt.append(("Idle", time, next_arrival))
            time = next_arrival
            continue

        # Lower priority number means higher priority
        p = min(available, key=lambda x: (x["priority"], x["arrival"], x["pid"]))
        start = time
        time += p["burst"]
        completion[p["pid"]] = time
        gantt.append((p["pid"], start, time))
        remaining.remove(p)

    return calculate_metrics(processes, completion) + (gantt,)


def round_robin(processes, quantum):
    from collections import deque

    procs = sorted(processes, key=lambda p: (p["arrival"], p["pid"]))
    remaining = {p["pid"]: p["burst"] for p in procs}
    completion = {}
    gantt = []
    queue = deque()
    time = 0
    i = 0

    while len(completion) < len(procs):
        while i < len(procs) and procs[i]["arrival"] <= time:
            queue.append(procs[i])
            i += 1

        if not queue:
            if i < len(procs):
                next_arrival = procs[i]["arrival"]
                gantt.append(("Idle", time, next_arrival))
                time = next_arrival
                continue
            break

        p = queue.popleft()
        pid = p["pid"]
        start = time
        run_time = min(quantum, remaining[pid])
        time += run_time
        remaining[pid] -= run_time
        gantt.append((pid, start, time))

        while i < len(procs) and procs[i]["arrival"] <= time:
            queue.append(procs[i])
            i += 1

        if remaining[pid] > 0:
            queue.append(p)
        else:
            completion[pid] = time

    return calculate_metrics(processes, completion) + (gantt,)
