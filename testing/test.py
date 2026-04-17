import calendar
from datetime import datetime
import json
import os

FILE_NAME = "tasks.json"


# ------------------ FILE HANDLING ------------------ #
def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return {}


def save_tasks(tasks):
    with open(FILE_NAME, "w") as f:
        json.dump(tasks, f, indent=4)


# ------------------ DISPLAY ------------------ #
def display_calendar(year, month, tasks):
    if month < 1 or month > 12:
        print("Invalid month.")
        return

    print(f"\n--- {calendar.month_name[month]} {year} ---")
    print(calendar.TextCalendar().formatmonth(year, month))

    print("Scheduled Tasks:")
    found = False

    for date, task_list in tasks.items():
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
        except:
            continue

        if d.year == year and d.month == month:
            for task in task_list:
                due = f"(Due: {task['due']})" if task['due'] else "(No due time)"
                print(f"{date} - {task['desc']} {due}")
                found = True

    if not found:
        print("No tasks this month.")


# ------------------ ADD TASK ------------------ #
def add_task(tasks):
    date = input("Enter date (YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format.")
        return

    desc = input("Task description: ").strip()
    due = input("Due time (optional): ").strip()

    if date not in tasks:
        tasks[date] = []

    tasks[date].append({
        "desc": desc,
        "due": due if due else None
    })

    save_tasks(tasks)
    print("Task saved!")


# ------------------ MAIN LOOP ------------------ #
def main():
    tasks = load_tasks()

    while True:
        print("\n==== TASK CALENDAR ====")
        print("1. View Calendar")
        print("2. Add Task")
        print("3. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            try:
                year = int(input("Year: "))
                month = int(input("Month (1-12): "))
                display_calendar(year, month, tasks)
            except ValueError:
                print("Invalid number.")

        elif choice == "2":
            add_task(tasks)

        elif choice == "3":
            print("Goodbye.")
            break

        else:
            print("Invalid option.")


# ------------------ RUN ------------------ #
if __name__ == "__main__":
    main()