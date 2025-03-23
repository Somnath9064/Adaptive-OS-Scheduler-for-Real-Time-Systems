import heapq
import time
import matplotlib.pyplot as plt
import seaborn as sns

# Global clock
global_clock = 0

# Time quantums for different queues
TIME_Q1 = 3  # High Priority
TIME_Q2 = 2  # Medium Priority
TIME_Q3 = 1  # Low Priority

class Task:
    def __init__(self, task_id, arrival_time, deadline, workload, priority=None):
        self.task_id = task_id
        self.arrival_time = arrival_time
        self.deadline = deadline
        self.workload = workload
        self.remaining_workload = workload
        self.priority = priority
        self.completion_time = 0
        self.executions = []  # To track Gantt chart timings

    def __repr__(self):
        return (f"Task(id={self.task_id}, arrival={self.arrival_time}, "
                f"deadline={self.deadline}, workload={self.workload}, "
                f"priority={self.priority})")

def adjust_priority(task, current_time, system_load):
    time_left = task.deadline - current_time
    priority = max(1, time_left - int(system_load * 5))  # Higher priority for tighter deadlines
    return priority

class Scheduler:
    def __init__(self):
        self.q1 = []  # High Priority Queue
        self.q2 = []  # Medium Priority Queue
        self.q3 = []  # Low Priority Queue
        self.result = []
        self.preempted_tasks = []
        self.missed_deadlines = []
        self.idle_time = 0
        self.gantt_data = []
        self.cpu_load_data = []

    def add_task(self, task):
        if task.priority > 100:
            self.q1.append(task)
        elif 50 < task.priority <= 100:
            self.q2.append(task)
        else:
            self.q3.append(task)

    def simulate_cpu_load(self, t):
        return 0.2 + 0.6 * (0.5 if 20 <= t <= 30 else 0.2)

    def schedule_queue(self, queue, time_quantum):
        global global_clock
        queue.sort(key=lambda p: p.arrival_time)
        i = 0
        while queue:
            task = queue[i % len(queue)]
            if task.arrival_time <= global_clock:
                exec_time = min(time_quantum, task.remaining_workload)
                print(f"Time {global_clock}: Executing Task {task.task_id} for {exec_time} units.")
                task.executions.append((global_clock, global_clock + exec_time))
                global_clock += exec_time
                task.remaining_workload -= exec_time

                if task.remaining_workload <= 0:
                    task.completion_time = global_clock
                    self.result.append(task)
                    queue.remove(task)
                    i = -1  # Reset to first item in queue
            else:
                global_clock += 1
            i += 1

    def run(self, total_time=50):
        global global_clock  # Declare global_clock as a global variable
        global_clock = 0  # Reset global_clock at the start of the simulation
        print("\n--- Simulation Start ---\n")
        while global_clock < total_time:
            # Record CPU load for visualization
            cpu_load = self.simulate_cpu_load(global_clock)
            self.cpu_load_data.append(cpu_load)

            # Update priorities for tasks in all queues
            for queue in [self.q1, self.q2, self.q3]:
                for task in queue:
                    task.priority = adjust_priority(task, global_clock, cpu_load)

            # Schedule queues in priority order
            print("Scheduling Queue 1 (High Priority)...")
            self.schedule_queue(self.q1, TIME_Q1)

            print("Scheduling Queue 2 (Medium Priority)...")
            self.schedule_queue(self.q2, TIME_Q2)

            print("Scheduling Queue 3 (Low Priority)...")
            self.schedule_queue(self.q3, TIME_Q3)

            # Check for idle time
            if not self.q1 and not self.q2 and not self.q3:
                print(f"Time {global_clock}: CPU idle.")
                self.gantt_data.append(("IDLE", global_clock, global_clock + 1))
                self.idle_time += 1
                global_clock += 1

        print("\n--- Simulation End ---\n")
        self.display_results()
        self.visualize()

    def display_results(self):
        print("\nTask ID\tArrival\tDeadline\tWorkload\tCompletion\tWaiting")
        total_wait = 0
        total_turnaround = 0

        for task in self.result:
            waiting_time = task.completion_time - task.arrival_time - task.workload
            turnaround_time = task.completion_time - task.arrival_time
            total_wait += waiting_time
            total_turnaround += turnaround_time
            print(f"{task.task_id}\t{task.arrival_time}\t{task.deadline}\t\t{task.workload}\t\t{task.completion_time}\t\t{waiting_time}")

        n = len(self.result)
        if n > 0:
            print(f"\nAverage Waiting Time: {total_wait / n:.2f}")
            print(f"Average Turnaround Time: {total_turnaround / n:.2f}")
            print(f"CPU Idle Time: {self.idle_time} units")
            print(f"Task Completion Rate: {n / (n + len(self.missed_deadlines)) * 100:.2f}%")

    def visualize(self):
        # Gantt Chart
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = sns.color_palette("tab10", len(self.result))

        for idx, task in enumerate(self.result):
            for start, end in task.executions:
                ax.barh(f'Task {task.task_id}', end - start, left=start, color=colors[idx])

        ax.set_xlabel("Time")
        ax.set_ylabel("Tasks")
        ax.set_title("Gantt Chart - Adaptive Multilevel Queue Scheduler")
        plt.grid(True)
        plt.show()

        # CPU Load Over Time
        plt.figure(figsize=(10, 5))
        plt.plot(range(len(self.cpu_load_data)), self.cpu_load_data, label="CPU Load", color="blue")
        plt.xlabel("Time Units")
        plt.ylabel("CPU Load")
        plt.title("CPU Load Over Time")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()

# Sample usage:
if __name__ == "__main__":
    scheduler = Scheduler()
    n = int(input("Enter number of tasks: "))
    for i in range(n):
        task_id = input(f"\nEnter Task ID for task {i+1}: ")
        arrival_time = int(input("Enter Arrival Time: "))
        deadline = int(input("Enter Deadline: "))
        workload = int(input("Enter Workload: "))
        priority = int(input("Enter Priority: "))
        scheduler.add_task(Task(task_id, arrival_time, deadline, workload, priority))

    scheduler.run()
