import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

def initialize_db():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            priority INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_task(title, due_date, priority):
    if not title or not due_date or not priority:
        messagebox.showerror("Error", "All fields are required!")
        return
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, due_date, priority) VALUES (?, ?, ?)", (title, due_date, priority))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Task added successfully!")
    refresh_task_list()

def fetch_tasks():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def refresh_task_list():
    for row in task_tree.get_children():
        task_tree.delete(row)
    for task in fetch_tasks():
        task_tree.insert("", "end", values=task)

def delete_task():
    selected_item = task_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No task selected!")
        return
    task_id = task_tree.item(selected_item, "values")[0]
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Task deleted successfully!")
    refresh_task_list()

def add_task_window():
    def submit_task():
        title = title_entry.get()
        due_date = due_date_entry.get()
        priority = priority_combobox.get()
        add_task(title, due_date, priority)
        add_window.destroy()

    add_window = tk.Toplevel(root)
    add_window.title("Add Task")
    add_window.geometry("300x200")

    tk.Label(add_window, text="Title:").pack(pady=5)
    title_entry = tk.Entry(add_window)
    title_entry.pack(pady=5)

    tk.Label(add_window, text="Due Date (YYYY-MM-DD):").pack(pady=5)
    due_date_entry = tk.Entry(add_window)
    due_date_entry.pack(pady=5)

    tk.Label(add_window, text="Priority (1-5):").pack(pady=5)
    priority_combobox = ttk.Combobox(add_window, values=[1, 2, 3, 4, 5])
    priority_combobox.pack(pady=5)

    tk.Button(add_window, text="Add Task", command=submit_task).pack(pady=10)

# Initialize main window
root = tk.Tk()
root.title("Smart To-Do App")
root.geometry("500x400")

# Task list display
task_tree = ttk.Treeview(root, columns=("ID", "Title", "Due Date", "Priority"), show="headings")
task_tree.heading("ID", text="ID")
task_tree.heading("Title", text="Title")
task_tree.heading("Due Date", text="Due Date")
task_tree.heading("Priority", text="Priority")
task_tree.pack(fill=tk.BOTH, expand=True, pady=10)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Add Task", command=add_task_window).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Refresh", command=refresh_task_list).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Delete Task", command=delete_task).pack(side=tk.LEFT, padx=5)

# Initialize database and load tasks
initialize_db()
refresh_task_list()

# Run the application
root.mainloop()
