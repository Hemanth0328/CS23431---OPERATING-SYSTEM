import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os


class FileCompressionScheduler:
    def __init__(self):
        self.files = []
        self.burst_times = []

    def add_file(self, file_name, burst_time):
        self.files.append(file_name)
        self.burst_times.append(burst_time)

    def clear_files(self):
        self.files = []
        self.burst_times = []

    def fcfs(self):
        n = len(self.burst_times)
        waiting_time = [0] * n
        turnaround_time = [0] * n

        waiting_time[0] = 0
        for i in range(1, n):
            waiting_time[i] = self.burst_times[i - 1] + waiting_time[i - 1]

        for i in range(n):
            turnaround_time[i] = self.burst_times[i] + waiting_time[i]

        avg_wait = sum(waiting_time) / n
        avg_tat = sum(turnaround_time) / n
        return waiting_time, turnaround_time, avg_wait, avg_tat

    def sjf(self):
        n = len(self.burst_times)
        waiting_time = [0] * n
        turnaround_time = [0] * n
        sorted_indices = sorted(range(n), key=lambda k: self.burst_times[k])

        for i in range(1, n):
            waiting_time[sorted_indices[i]] = (
                    self.burst_times[sorted_indices[i - 1]] +
                    waiting_time[sorted_indices[i - 1]]
            )

        for i in range(n):
            turnaround_time[i] = self.burst_times[i] + waiting_time[i]

        avg_wait = sum(waiting_time) / n
        avg_tat = sum(turnaround_time) / n
        return waiting_time, turnaround_time, avg_wait, avg_tat

    def round_robin(self, quantum):
        n = len(self.burst_times)
        waiting_time = [0] * n
        remaining = self.burst_times.copy()
        time = 0
        queue = []

        while True:
            done = True
            for i in range(n):
                if remaining[i] > 0:
                    done = False
                    if remaining[i] > quantum:
                        time += quantum
                        remaining[i] -= quantum
                        queue.append(i)
                    else:
                        time += remaining[i]
                        waiting_time[i] = time - self.burst_times[i]
                        remaining[i] = 0
            if done:
                break

        turnaround_time = [self.burst_times[i] + waiting_time[i] for i in range(n)]
        avg_wait = sum(waiting_time) / n
        avg_tat = sum(turnaround_time) / n
        return waiting_time, turnaround_time, avg_wait, avg_tat

class CompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Compression Scheduler")
        self.root.geometry("800x600")
        self.scheduler = FileCompressionScheduler()

        self.create_widgets()
        self.setup_style()

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))

    def create_widgets(self):
        # File Selection Panel
        file_frame = ttk.LabelFrame(self.root, text="File Selection")
        file_frame.pack(pady=10, padx=10, fill='x')

        self.file_list = tk.Listbox(file_frame, height=5, selectmode=tk.EXTENDED)
        self.file_list.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(pady=2)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).pack(pady=2)

        # Algorithm Selection
        algo_frame = ttk.LabelFrame(self.root, text="Scheduling Algorithms")
        algo_frame.pack(pady=10, padx=10, fill='x')

        ttk.Button(algo_frame, text="FCFS", command=self.run_fcfs).pack(side=tk.LEFT, padx=5)
        ttk.Button(algo_frame, text="SJF", command=self.run_sjf).pack(side=tk.LEFT, padx=5)
        ttk.Button(algo_frame, text="Round Robin", command=self.run_rr).pack(side=tk.LEFT, padx=5)

        # Algorithm Suggestion Label
        self.suggestion_label = ttk.Label(self.root, text="Algorithm Suggestion: None", style='Header.TLabel')
        self.suggestion_label.pack(pady=10)

        # Visualization Frame
        self.vis_frame = ttk.Frame(self.root)
        self.vis_frame.pack(pady=10, padx=10, fill='both', expand=True)

    def add_files(self):
        files = filedialog.askopenfilenames()
        if files:
            for f in files:
                burst_time = np.random.randint(1, 10)  # Simulated compression time
                self.scheduler.add_file(os.path.basename(f), burst_time)
                self.file_list.insert(tk.END, f"{os.path.basename(f)} (BT: {burst_time})")
            self.suggest_algorithm()

    def clear_files(self):
        self.scheduler.clear_files()
        self.file_list.delete(0, tk.END)
        self.suggestion_label.config(text="Algorithm Suggestion: None")

    def suggest_algorithm(self):
        if not self.scheduler.files:
            return

        burst_times = self.scheduler.burst_times
        n = len(burst_times)

        # Analyze burst times
        if n <= 5:
            suggestion = "FCFS (Few files, simple and fair)"
        elif max(burst_times) - min(burst_times) <= 2:
            suggestion = "Round Robin (Similar burst times, fair scheduling)"
        else:
            suggestion = "SJF (Optimal for minimizing waiting time)"

        self.suggestion_label.config(text=f"Algorithm Suggestion: {suggestion}")

    def run_fcfs(self):
        if not self.scheduler.files:
            messagebox.showerror("Error", "No files selected!")
            return
        wt, tat, avg_wt, avg_tat = self.scheduler.fcfs()
        self.plot_results("FCFS", wt, tat, avg_wt, avg_tat)

    def run_sjf(self):
        if not self.scheduler.files:
            messagebox.showerror("Error", "No files selected!")
            return
        wt, tat, avg_wt, avg_tat = self.scheduler.sjf()
        self.plot_results("SJF", wt, tat, avg_wt, avg_tat)

    def run_rr(self):
        if not self.scheduler.files:
            messagebox.showerror("Error", "No files selected!")
            return
        quantum = simpledialog.askinteger("Round Robin", "Enter time quantum:", parent=self.root)
        if quantum:
            wt, tat, avg_wt, avg_tat = self.scheduler.round_robin(quantum)
            self.plot_results(f"Round Robin (Q={quantum})", wt, tat, avg_wt, avg_tat)

    def plot_results(self, algorithm, wt, tat, avg_wt, avg_tat):
        # Clear previous visualization
        for widget in self.vis_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

        # Plot waiting times
        ax1.bar(range(len(wt)), wt, color='skyblue')
        ax1.set_title(f'{algorithm} Waiting Times\nAvg: {avg_wt:.2f}')
        ax1.set_xlabel('Files')
        ax1.set_ylabel('Waiting Time')

        # Plot turnaround times
        ax2.bar(range(len(tat)), tat, color='lightgreen')
        ax2.set_title(f'{algorithm} Turnaround Times\nAvg: {avg_tat:.2f}')
        ax2.set_xlabel('Files')
        ax2.set_ylabel('Turnaround Time')

        # Embed plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.vis_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionApp(root)
    root.mainloop()