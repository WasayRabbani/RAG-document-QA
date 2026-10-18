# Run from backend/:  python debug_trace.py
import json, os
from ingestion.pdf_loader import PDFLoader
from ingestion.text_chunker import TextChunker

PDF = "../messy_sample.pdf"
OUT = "debug_out"
os.makedirs(OUT, exist_ok=True)

def dump(name, obj):
    path = f"{OUT}/{name}"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)
    print(f"   full output saved to backend/{path}")

# ---------- STAGE 1: extraction ----------
print("STAGE 1: PDFLoader.load_pdf()")
pages = PDFLoader(PDF).load_pdf()
print("   type:", type(pages).__name__, "| length:", len(pages))
first = pages[0] if isinstance(pages, list) else next(iter(pages.items()))
print("   first item type:", type(first).__name__)
print("   first item preview:", repr(first)[:600])
dump("stage1_pages.json", pages)

# ---------- STAGE 2: chunking ----------
print("\nSTAGE 2: TextChunker.chunking()")
chunks = TextChunker(pages).chunking()
print("   type:", type(chunks).__name__, "| chunks:", len(chunks))
c = chunks[0]
print("   chunk keys:", list(c.keys()) if isinstance(c, dict) else type(c).__name__)

if isinstance(c, dict) and "text" in c:
    lengths = sorted(len(x["text"]) for x in chunks)
    print(f"   chunk length: min={lengths[0]} median={lengths[len(lengths)//2]} max={lengths[-1]}")
    print(f"   tiny chunks (<100 chars): {sum(l < 100 for l in lengths)}")
    print(f"   chunks containing '?': {sum('?' in x['text'] for x in chunks)}")
    pages_seen = sorted({x.get('page') for x in chunks})
    print("   pages that produced chunks:", pages_seen)
    print("\n   --- 3 sample chunks (every ~third of the document) ---")
    for i in (0, len(chunks)//3, 2*len(chunks)//3):
        print(f"\n   [chunk {i}] page={chunks[i].get('page')}")
        print("  ", chunks[i]["text"][:400].replace("\n", "\n   "))
dump("stage2_chunks.json", chunks)