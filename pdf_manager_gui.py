import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import json, re
from pathlib import Path
from PyPDF2 import PdfMerger

CONFIG = "priority_config.json"
NUMBER_RE = re.compile(r"(\d+)")

def load_config():
    if Path(CONFIG).exists():
        data = json.loads(Path(CONFIG).read_text())
        return data.get("keyword_order", []), data.get("numeric_sort", "asc")
    return [], "asc"

def save_config(priorities, numeric_sort="asc"):
    with open(CONFIG, "w") as f:
        json.dump({
            "keyword_order": priorities,
            "numeric_sort": numeric_sort
        }, f, indent=2)
    messagebox.showinfo("Saved", "Priority list saved!")

def make_sort_key(priorities, numeric_sort):
    prio_index = {kw: i for i, kw in enumerate(priorities)}
    def key(path: Path):
        name = path.stem
        m = NUMBER_RE.search(name)
        num = int(m.group(1)) if m else 0
        bucket = next((prio_index[k] for k in priorities if k in name), len(priorities))
        return (bucket, num if numeric_sort=="asc" else -num, name.lower())
    return key

class PDFManagerGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # load or init
        self.priorities, self.numeric_sort = load_config()
        self.selected_files = []

        # Priority editor
        prio_frame = tk.LabelFrame(self, text="Keyword Priority", padx=5, pady=5)
        prio_frame.pack(fill=tk.X, pady=5)
        self.lb_prio = tk.Listbox(prio_frame, height=5)
        self.lb_prio.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._refresh_prio()
        btns = tk.Frame(prio_frame)
        btns.pack(side=tk.RIGHT, padx=5)
        for txt, cmd in [
            ("Add", self._add_kw), ("Remove", self._rm_kw),
            ("Up", self._up_kw), ("Down", self._dn_kw),
            ("Save", lambda: save_config(self.priorities, self.numeric_sort))
        ]:
            b = tk.Button(btns, text=txt, width=8, command=cmd)
            b.pack(pady=2)

        # File chooser + merge
        file_frame = tk.LabelFrame(self, text="Merge PDFs", padx=5, pady=5)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.lb_files = tk.Listbox(file_frame, height=8)
        self.lb_files.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_btns = tk.Frame(file_frame)
        file_btns.pack(side=tk.RIGHT, padx=5, fill=tk.Y)
        tk.Button(file_btns, text="Select PDFs…", width=12, command=self._pick_files).pack(pady=5)
        tk.Button(file_btns, text="Merge PDFs", width=12, command=self._merge).pack(pady=5)

    def _refresh_prio(self):
        self.lb_prio.delete(0, tk.END)
        for kw in self.priorities:
            self.lb_prio.insert(tk.END, kw)

    def _add_kw(self):
        kw = simpledialog.askstring("New keyword", "Enter keyword to prioritize:")
        if kw:
            self.priorities.append(kw)
            self._refresh_prio()

    def _rm_kw(self):
        sel = self.lb_prio.curselection()
        if sel:
            self.priorities.pop(sel[0])
            self._refresh_prio()

    def _up_kw(self):
        sel = self.lb_prio.curselection()
        if sel and sel[0]>0:
            i = sel[0]
            self.priorities[i-1], self.priorities[i] = self.priorities[i], self.priorities[i-1]
            self._refresh_prio()
            self.lb_prio.select_set(i-1)

    def _dn_kw(self):
        sel = self.lb_prio.curselection()
        if sel and sel[0]<len(self.priorities)-1:
            i = sel[0]
            self.priorities[i+1], self.priorities[i] = self.priorities[i], self.priorities[i+1]
            self._refresh_prio()
            self.lb_prio.select_set(i+1)

    def _pick_files(self):
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDFs","*.pdf")])
        # Add new selections, skip duplicates
        for f in files:
            p = Path(f)
            if p not in self.selected_files:
                self.selected_files.append(p)
        self._refresh_file_list()



    def _refresh_file_list(self):
        key = make_sort_key(self.priorities, self.numeric_sort)
        self.selected_files.sort(key=key)
        self.lb_files.delete(0, tk.END)
        for p in self.selected_files:
            self.lb_files.insert(tk.END, p.name)

    def _merge(self):
        if not self.selected_files:
            return messagebox.showwarning("No files", "Please select some PDFs first!")
        out = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")],
            title="Save merged PDF as…") 
        if not out:
            return
        merger = PdfMerger()
        for p in self.selected_files:
            merger.append(str(p))
        merger.write(out)
        merger.close()
        messagebox.showinfo("Done", f"Merged {len(self.selected_files)} →\n{out}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PDF Manager (Priority + Merge)")
    PDFManagerGUI(root)
    root.mainloop()
