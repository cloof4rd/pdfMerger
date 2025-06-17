import tkinter as tk
from tkinter import simpledialog, messagebox
import json
from pathlib import Path

CONFIG = "priority_config.json"

def load_priorities():
    if Path(CONFIG).exists():
        return json.loads(Path(CONFIG).read_text()).get("keyword_order", [])
    return []

def save_priorities(lst):
    with open(CONFIG, "w") as f:
        json.dump({"keyword_order": lst, "numeric_sort": "asc"}, f, indent=2)
    messagebox.showinfo("Saved", "Priority list saved!")

class PriorityEditor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(padx=10, pady=10)
        self.priorities = load_priorities()

        self.listbox = tk.Listbox(self, height=8, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._refresh()

        btns = tk.Frame(self)
        btns.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        for (text, cmd) in [
            ("Add", self.add_item),
            ("Remove", self.remove_item),
            ("Up", self.move_up),
            ("Down", self.move_down),
            ("Save", lambda: save_priorities(self.priorities))
        ]:
            b = tk.Button(btns, text=text, width=10, command=cmd)
            b.pack(pady=2)

    def _refresh(self):
        self.listbox.delete(0, tk.END)
        for kw in self.priorities:
            self.listbox.insert(tk.END, kw)

    def add_item(self):
        kw = simpledialog.askstring("New keyword", "Enter keyword to prioritize:")
        if kw:
            self.priorities.append(kw)
            self._refresh()

    def remove_item(self):
        sel = self.listbox.curselection()
        if sel:
            self.priorities.pop(sel[0])
            self._refresh()

    def move_up(self):
        sel = self.listbox.curselection()
        if sel and sel[0] > 0:
            i = sel[0]
            self.priorities[i-1], self.priorities[i] = self.priorities[i], self.priorities[i-1]
            self._refresh()
            self.listbox.select_set(i-1)

    def move_down(self):
        sel = self.listbox.curselection()
        if sel and sel[0] < len(self.priorities)-1:
            i = sel[0]
            self.priorities[i+1], self.priorities[i] = self.priorities[i], self.priorities[i+1]
            self._refresh()
            self.listbox.select_set(i+1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Edit PDF Merge Priority")
    PriorityEditor(root)
    root.mainloop()
