import tkinter as tk
from tkinter import ttk, messagebox
import scheduler


# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("CPU Scheduling Visualizer")
root.geometry("1100x850")
root.minsize(900, 700)
root.configure(bg="#eef2f7")

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    rowheight=28,
    font=("Arial", 10)
)
style.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold")
)
style.configure(
    "TNotebook.Tab",
    font=("Arial", 11, "bold"),
    padding=10
)

title = tk.Label(
    root,
    text="CPU SCHEDULING VISUALIZER",
    font=("Arial", 22, "bold"),
    bg="#eef2f7",
    fg="#1e3a8a"
)
title.pack(pady=15)


# ---------------- NOTEBOOK ----------------

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=15, pady=10)

input_tab = tk.Frame(notebook, bg="#eef2f7")
gantt_tab = tk.Frame(notebook, bg="#eef2f7")
graphs_tab = tk.Frame(notebook, bg="#eef2f7")

notebook.add(input_tab, text="Input & Results")
notebook.add(gantt_tab, text="Gantt Charts")
notebook.add(graphs_tab, text="Comparison Graphs")


# ---------------- PROCESS INPUT ----------------

input_frame = tk.LabelFrame(
    input_tab,
    text="Enter Process Details",
    font=("Arial", 12, "bold"),
    bg="#eef2f7",
    padx=10,
    pady=10
)
input_frame.pack(fill="x", padx=15, pady=10)

labels = [
    "Process ID",
    "Arrival Time",
    "Burst Time",
    "Priority"
]

entries = []

for i, label in enumerate(labels):
    tk.Label(
        input_frame,
        text=label,
        font=("Arial", 10),
        bg="#eef2f7"
    ).grid(row=0, column=i, padx=8, pady=5)

    entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
    entry.grid(row=1, column=i, padx=8, pady=5)
    entries.append(entry)

pid_entry, arrival_entry, burst_entry, priority_entry = entries


# ---------------- PROCESS TABLE ----------------

process_frame = tk.LabelFrame(
    input_tab,
    text="Process List",
    font=("Arial", 12, "bold"),
    bg="#eef2f7",
    padx=10,
    pady=10
)
process_frame.pack(fill="x", padx=15, pady=8)

process_table = ttk.Treeview(
    process_frame,
    columns=("PID", "Arrival", "Burst", "Priority"),
    show="headings",
    height=4
)

for col in ("PID", "Arrival", "Burst", "Priority"):
    process_table.heading(col, text=col)
    process_table.column(col, width=150, anchor="center")

process_table.pack(fill="x")


# ---------------- BUTTONS ----------------

def add_process():
    try:
        pid = pid_entry.get().strip()
        arrival = int(arrival_entry.get())
        burst = int(burst_entry.get())
        priority = int(priority_entry.get())

        if not pid:
            raise ValueError("Enter Process ID.")

        if any(
            process_table.item(row)["values"][0] == pid
            for row in process_table.get_children()
        ):
            raise ValueError("Process ID already exists.")

        if arrival < 0 or burst <= 0 or priority < 0:
            raise ValueError(
                "Arrival must be >= 0, Burst > 0, Priority >= 0."
            )

        process_table.insert(
            "", "end",
            values=(pid, arrival, burst, priority)
        )

        for entry in entries:
            entry.delete(0, tk.END)

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))


def delete_process():
    selected = process_table.selection()

    if not selected:
        messagebox.showwarning(
            "Selection",
            "Please select a process to delete."
        )
        return

    for item in selected:
        process_table.delete(item)


# ---------------- CONTROL FRAME ----------------

control_frame = tk.Frame(input_tab, bg="#eef2f7")
control_frame.pack(pady=8)

tk.Label(
    control_frame,
    text="Time Quantum:",
    bg="#eef2f7",
    font=("Arial", 10, "bold")
).pack(side="left", padx=5)

quantum_entry = tk.Entry(control_frame, width=8)
quantum_entry.insert(0, "2")
quantum_entry.pack(side="left", padx=5)

tk.Button(
    control_frame,
    text="Add Process",
    command=add_process,
    bg="#2563eb",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=12
).pack(side="left", padx=5)

tk.Button(
    control_frame,
    text="Delete Process",
    command=delete_process,
    bg="#d97706",
    fg="white",
    padx=12
).pack(side="left", padx=5)


# ---------------- RESULTS TABLE ----------------

result_frame = tk.LabelFrame(
    input_tab,
    text="Algorithm Comparison Results",
    font=("Arial", 12, "bold"),
    bg="#eef2f7",
    padx=10,
    pady=10
)
result_frame.pack(fill="both", expand=True, padx=15, pady=10)

results_table = ttk.Treeview(
    result_frame,
    columns=(
        "Algorithm",
        "Average Waiting Time",
        "Average Turnaround Time"
    ),
    show="headings",
    height=5
)

results_table.heading("Algorithm", text="Algorithm")
results_table.heading(
    "Average Waiting Time",
    text="Average Waiting Time"
)
results_table.heading(
    "Average Turnaround Time",
    text="Average Turnaround Time"
)

results_table.column("Algorithm", width=180, anchor="center")
results_table.column(
    "Average Waiting Time", width=230, anchor="center"
)
results_table.column(
    "Average Turnaround Time", width=250, anchor="center"
)

results_table.pack(fill="both", expand=True)


# ---------------- GANTT CHART ----------------

gantt_canvas = tk.Canvas(
    gantt_tab,
    bg="white",
    height=600,
    highlightthickness=0
)
gantt_scroll = ttk.Scrollbar(
    gantt_tab,
    orient="vertical",
    command=gantt_canvas.yview
)
gantt_canvas.configure(yscrollcommand=gantt_scroll.set)

gantt_scroll.pack(side="right", fill="y")
gantt_canvas.pack(side="left", fill="both", expand=True)


# ---------------- COMPARISON GRAPHS ----------------

graph_canvas = tk.Canvas(
    graphs_tab,
    bg="white",
    highlightthickness=0
)
graph_canvas.pack(fill="both", expand=True, padx=10, pady=10)


# ---------------- DRAW GANTT CHARTS ----------------

def draw_gantt(all_results):

    gantt_canvas.delete("all")

    colors = [
        "#60a5fa",
        "#34d399",
        "#fbbf24",
        "#f472b6",
        "#a78bfa",
        "#fb923c"
    ]

    y = 40

    for algorithm, data in all_results.items():

        gantt = data[3]

        gantt_canvas.create_text(
            20, y,
            text=algorithm,
            anchor="w",
            font=("Arial", 13, "bold"),
            fill="#1e3a8a"
        )

        y += 35

        if not gantt:
            continue

        total_time = max(item[2] for item in gantt)
        scale = max(25, 850 / max(total_time, 1))

        x = 30

        for index, (pid, start, end) in enumerate(gantt):

            width = (end - start) * scale

            color = (
                "#d1d5db"
                if pid == "Idle"
                else colors[index % len(colors)]
            )

            gantt_canvas.create_rectangle(
                x, y,
                x + width, y + 45,
                fill=color,
                outline="#374151",
                width=1
            )

            gantt_canvas.create_text(
                x + width / 2,
                y + 22,
                text=pid,
                font=("Arial", 10, "bold")
            )

            gantt_canvas.create_text(
                x, y + 62,
                text=str(start),
                font=("Arial", 9)
            )

            x += width

        gantt_canvas.create_text(
            x, y + 62,
            text=str(gantt[-1][2]),
            font=("Arial", 9)
        )

        y += 110

    gantt_canvas.configure(
        scrollregion=gantt_canvas.bbox("all")
    )


# ---------------- DRAW COMPARISON GRAPHS ----------------

def draw_graphs(all_results):

    graph_canvas.delete("all")

    algorithms = list(all_results.keys())

    waiting = [
        all_results[name][1] for name in algorithms
    ]

    turnaround = [
        all_results[name][2] for name in algorithms
    ]

    width = max(graph_canvas.winfo_width(), 800)

    def draw_bar_chart(title, values, y_start, bar_color):

        graph_canvas.create_text(
            20, y_start,
            text=title,
            anchor="w",
            font=("Arial", 14, "bold"),
            fill="#1e3a8a"
        )

        max_value = max(values) if max(values) > 0 else 1

        for i, (name, value) in enumerate(
            zip(algorithms, values)
        ):

            y = y_start + 45 + i * 42
            bar_width = (value / max_value) * (width - 250)

            graph_canvas.create_text(
                20, y + 10,
                text=name,
                anchor="w",
                font=("Arial", 10, "bold")
            )

            graph_canvas.create_rectangle(
                145, y,
                145 + bar_width, y + 22,
                fill=bar_color,
                outline=""
            )

            graph_canvas.create_text(
                155 + bar_width, y + 11,
                text=f"{value:.2f}",
                anchor="w",
                font=("Arial", 10)
            )

    draw_bar_chart(
        "Average Waiting Time",
        waiting,
        25,
        "#60a5fa"
    )

    draw_bar_chart(
        "Average Turnaround Time",
        turnaround,
        260,
        "#34d399"
    )

    best_wait = algorithms[waiting.index(min(waiting))]
    best_turn = algorithms[turnaround.index(min(turnaround))]

    graph_canvas.create_text(
        20, 500,
        text=f"Lowest Average Waiting Time: {best_wait}",
        anchor="w",
        font=("Arial", 11, "bold"),
        fill="#15803d"
    )

    graph_canvas.create_text(
        20, 530,
        text=f"Lowest Average Turnaround Time: {best_turn}",
        anchor="w",
        font=("Arial", 11, "bold"),
        fill="#15803d"
    )


# ---------------- RUN ALL ALGORITHMS ----------------

def run_simulation():

    try:

        rows = process_table.get_children()

        if not rows:
            messagebox.showwarning(
                "Input Required",
                "Please add at least one process."
            )
            return

        processes = []

        for row in rows:

            values = process_table.item(row)["values"]

            processes.append({
                "pid": str(values[0]),
                "arrival": int(values[1]),
                "burst": int(values[2]),
                "priority": int(values[3])
            })

        quantum = int(quantum_entry.get())

        if quantum <= 0:
            raise ValueError("Time Quantum must be positive.")

        algorithms = {
            "FCFS": scheduler.fcfs,
            "SJF": scheduler.sjf,
            "Priority": scheduler.priority_scheduling,
            "Round Robin": lambda p: scheduler.round_robin(
                p, quantum
            )
        }

        all_results = {}

        results_table.delete(
            *results_table.get_children()
        )

        for name, function in algorithms.items():

            result = function(processes)

            results, avg_wait, avg_turn, gantt = result

            all_results[name] = result

            results_table.insert(
                "",
                "end",
                values=(
                    name,
                    f"{avg_wait:.2f}",
                    f"{avg_turn:.2f}"
                )
            )

        draw_gantt(all_results)
        draw_graphs(all_results)

        notebook.select(input_tab)

        messagebox.showinfo(
            "Success",
            "All scheduling algorithms executed successfully!"
        )

    except ValueError as e:

        messagebox.showerror(
            "Input Error",
            str(e)
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Something went wrong:\n{e}"
        )


# ---------------- RUN AND RESET BUTTONS ----------------

def reset_all():

    process_table.delete(
        *process_table.get_children()
    )

    results_table.delete(
        *results_table.get_children()
    )

    gantt_canvas.delete("all")
    graph_canvas.delete("all")

    quantum_entry.delete(0, tk.END)
    quantum_entry.insert(0, "2")


bottom_frame = tk.Frame(input_tab, bg="#eef2f7")
bottom_frame.pack(pady=10)

tk.Button(
    bottom_frame,
    text="COMPARE ALGORITHMS",
    command=run_simulation,
    bg="#15803d",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=20,
    pady=8
).pack(side="left", padx=10)

tk.Button(
    bottom_frame,
    text="RESET ALL",
    command=reset_all,
    bg="#dc2626",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=20,
    pady=8
).pack(side="left", padx=10)


# ---------------- START APPLICATION ----------------

root.mainloop()
