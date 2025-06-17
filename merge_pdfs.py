import re
import json
import argparse
from pathlib import Path
from PyPDF2 import PdfMerger

# --- Load config ---
with open("priority_config.json", "r") as f:
    cfg = json.load(f)
priority = cfg.get("keyword_order", [])
numeric_sort = cfg.get("numeric_sort", "asc")
prio_index = {kw: i for i, kw in enumerate(priority)}
number_re = re.compile(r"(\d+)")

def sort_key(path: Path):
    name = path.stem
    m = number_re.search(name)
    num = int(m.group(1)) if m else 0
    bucket = next((prio_index[k] for k in priority if k in name), len(priority))
    return (bucket, num if numeric_sort == "asc" else -num, name.lower())

def main():
    p = argparse.ArgumentParser(description="Merge PDFs with custom keyword order")
    p.add_argument("folder", help="Folder containing your PDFs")
    p.add_argument("-o", "--output", default="merged_output.pdf", help="Output PDF filename")
    args = p.parse_args()

    paths = sorted(Path(args.folder).glob("*.pdf"), key=sort_key)
    merger = PdfMerger()
    for pdf in paths:
        merger.append(str(pdf))
    merger.write(args.output)
    merger.close()
    print(f"Merged {len(paths)} files into {args.output}")

if __name__ == "__main__":
    main()
