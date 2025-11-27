"""
Habit Tracker + Pomodoro CLI (Day 45)
Pure Python, stores data in habits.json
"""

import json
from pathlib import Path
from datetime import datetime, date, timedelta
import time
import csv
import os

DATA_FILE = Path("habits.json")

def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"habits": {}}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def today_str():
    return date.today().isoformat()

def parse_day(s):
    return datetime.strptime(s, "%Y-%m-%d").date()

def add_habit(name, data):
    name = name.strip()
    if not name:
        print("❗ Name cannot be empty.")
        return
    if name in data["habits"]:
        print("⚠ Habit already exists.")
        return
    data["habits"][name] = {"done_dates": []}
    save_data(data)
    print(f"✅ Added habit: {name}")

def remove_habit(name, data):
    if name in data["habits"]:
        del data["habits"][name]
        save_data(data)
        print(f"🗑 Removed habit: {name}")
    else:
        print("❌ Habit not found.")

def mark_done(name, data, on_date=None):
    if name not in data["habits"]:
        print("❌ Habit not found.")
        return
    d = on_date or today_str()
    if d in data["habits"][name]["done_dates"]:
        print("ℹ Already marked done for", d)
        return
    data["habits"][name]["done_dates"].append(d)
    data["habits"][name]["done_dates"].sort()
    save_data(data)
    print(f"✅ Marked {name} done for {d}")

def unmark_done(name, data, on_date=None):
    if name not in data["habits"]:
        print("❌ Habit not found.")
        return
    d = on_date or today_str()
    if d in data["habits"][name]["done_dates"]:
        data["habits"][name]["done_dates"].remove(d)
        save_data(data)
        print(f"↩ Unmarked {name} for {d}")
    else:
        print("ℹ No entry for", d)

def get_streak(done_dates):
    if not done_dates:
        return 0, 0  # current, best
    # convert to sorted date objects
    days = sorted(parse_day(d) for d in done_dates)
    best = 0
    current = 0
    streak = 0
    prev = None
    for d in days:
        if prev is None or (d - prev).days > 1:
            streak = 1
        else:
            streak += 1
        if streak > best:
            best = streak
        prev = d
    # current streak: count consecutive days up to today
    today = date.today()
    cur = 0
    d = today
    while True:
        if d.isoformat() in done_dates:
            cur += 1
            d = d - timedelta(days=1)
        else:
            break
    return cur, best

def summary(data):
    if not data["habits"]:
        print("ℹ No habits yet. Add one!")
        return
    print("\n📊 Habit Summary:")
    for name, info in data["habits"].items():
        total = len(info["done_dates"])
        cur, best = get_streak(info["done_dates"])
        last = info["done_dates"][-1] if info["done_dates"] else "—"
        print(f"\n• {name}")
        print(f"  - Total completions: {total}")
        print(f"  - Current streak: {cur} day(s)")
        print(f"  - Best streak: {best} day(s)")
        print(f"  - Last done: {last}")

def show_history(name, data, days=30):
    if name not in data["habits"]:
        print("❌ Habit not found.")
        return
    print(f"\n📜 History for '{name}':")
    dates = sorted(data["habits"][name]["done_dates"])
    if not dates:
        print("No entries yet.")
        return
    # show last N days
    cutoff = date.today() - timedelta(days=days)
    for d in dates:
        if parse_day(d) >= cutoff:
            print(" -", d)

def weekly_progress(name, data):
    if name not in data["habits"]:
        print("❌ Habit not found.")
        return
    counts = []
    today = date.today()
    for w in range(4):  # last 4 weeks
        start = today - timedelta(days=(w*7 + 6))
        end = today - timedelta(days=(w*7))
        cnt = sum(1 for d in data["habits"][name]["done_dates"] if start <= parse_day(d) <= end)
        counts.append((start.isoformat(), end.isoformat(), cnt))
    print(f"\n📈 Weekly progress for '{name}':")
    for s, e, c in counts[::-1]:
        print(f" {s} → {e} : {c} times")

def export_csv(name, data, filename=None):
    if name not in data["habits"]:
        print("❌ Habit not found.")
        return
    filename = filename or f"{name.replace(' ', '_')}_history.csv"
    rows = [["date"]]
    for d in sorted(data["habits"][name]["done_dates"]):
        rows.append([d])
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"📤 Exported history to {filename}")

def start_pomodoro(work_minutes=25, break_minutes=5, cycles=1):
    try:
        work = int(work_minutes)
        brk = int(break_minutes)
        cyc = int(cycles)
    except ValueError:
        print("❗ Provide integer minutes/cycles.")
        return
    print(f"\n🍅 Pomodoro: {cyc} cycle(s) — {work}m work / {brk}m break")
    for c in range(1, cyc+1):
        print(f"\n▶ Cycle {c} — Work for {work} minute(s). Focus!")
        countdown_minutes(work)
        print("\n⏸ Time for a break — Relax!")
        countdown_minutes(brk)
    print("\n✅ Pomodoro session complete! Great job.")

def countdown_minutes(minutes):
    total = minutes * 60
    try:
        while total > 0:
            m, s = divmod(total, 60)
            print(f"\rTime left: {m:02d}:{s:02d}", end="", flush=True)
            time.sleep(1)
            total -= 1
        print("\rTime left: 00:00")
    except KeyboardInterrupt:
        print("\n⏹ Pomodoro interrupted.")
        return

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def menu():
    data = load_data()
    while True:
        print("\n===================================")
        print("📅 Smart Habit Tracker + Pomodoro")
        print("===================================")
        print("1. Add habit")
        print("2. Remove habit")
        print("3. Mark habit done (today)")
        print("4. Mark habit done (date)")
        print("5. Unmark done (date)")
        print("6. View summary")
        print("7. View history (last 30 days)")
        print("8. Weekly progress")
        print("9. Export habit history (CSV)")
        print("10. Start Pomodoro")
        print("0. Exit")
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            name = input("Enter habit name: ").strip()
            add_habit(name, data)
        elif choice == "2":
            name = input("Enter habit name to remove: ").strip()
            remove_habit(name, data)
        elif choice == "3":
            name = input("Enter habit name to mark done: ").strip()
            mark_done(name, data)
        elif choice == "4":
            name = input("Enter habit name: ").strip()
            d = input("Enter date (YYYY-MM-DD): ").strip()
            # validate date
            try:
                parse_day(d)
                mark_done(name, data, on_date=d)
            except Exception:
                print("❗ Invalid date format.")
        elif choice == "5":
            name = input("Enter habit name: ").strip()
            d = input("Enter date to unmark (YYYY-MM-DD): ").strip()
            try:
                parse_day(d)
                unmark_done(name, data, on_date=d)
            except Exception:
                print("❗ Invalid date format.")
        elif choice == "6":
            summary(data)
        elif choice == "7":
            name = input("Enter habit name: ").strip()
            show_history(name, data, days=30)
        elif choice == "8":
            name = input("Enter habit name: ").strip()
            weekly_progress(name, data)
        elif choice == "9":
            name = input("Enter habit name: ").strip()
            export_csv(name, data)
        elif choice == "10":
            w = input("Work minutes (default 25): ").strip() or "25"
            b = input("Break minutes (default 5): ").strip() or "5"
            cyc = input("Cycles (default 1): ").strip() or "1"
            start_pomodoro(w, b, cyc)
        elif choice == "0":
            print("👋 Bye — keep building good habits!")
            break
        else:
            print("❗ Invalid choice. Try again.")
        input("\nPress Enter to continue...")
        clear_screen()

if __name__ == "__main__":
    menu()
