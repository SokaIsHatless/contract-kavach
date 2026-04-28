from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import shutil, uuid, os
from pathlib import Path
from claude_vision import analyze_contract
from rules import evaluate

try:
    import pypdfium2 as pdfium
    HAS_PDFIUM = True
except ImportError:
    HAS_PDFIUM = False

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MOCK_DIR = Path(__file__).parent.parent / "mock_contracts"
VALID_SAMPLES = {"worst_case", "sneaky", "mostly_fair"}


def pdf_page_count(path: str) -> int:
    if not HAS_PDFIUM:
        return 1
    doc = pdfium.PdfDocument(path)
    count = len(doc)
    doc.close()
    return count


def render_pdf_page(path: str, page_num: int) -> bytes:
    doc = pdfium.PdfDocument(path)
    page = doc[page_num - 1]
    bitmap = page.render(scale=2)
    pil_image = bitmap.to_pil()
    import io
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    doc.close()
    return buf.getvalue()


@app.post("/api/analyze")
async def analyze(files: list[UploadFile] = File(...)):
    paths = []
    uuids = []
    for f in files:
        uid = str(uuid.uuid4())
        dest = UPLOAD_DIR / f"{uid}_{f.filename}"
        with open(dest, "wb") as out:
            shutil.copyfileobj(f.file, out)
        paths.append(str(dest))
        uuids.append(uid)

    source_id = uuids[0]
    first_path = paths[0]
    is_pdf = first_path.lower().endswith(".pdf")

    if is_pdf and HAS_PDFIUM:
        total_pages = pdf_page_count(first_path)
    else:
        total_pages = len(paths)

    contract = analyze_contract(paths)
    flags = evaluate(contract)
    return {"contract": contract, "flags": flags, "source_id": source_id, "total_pages": total_pages, "is_pdf": is_pdf}


@app.get("/api/samples/{name}")
async def sample(name: str):
    if name not in VALID_SAMPLES:
        raise HTTPException(status_code=404, detail=f"Unknown sample '{name}'. Valid: {sorted(VALID_SAMPLES)}")
    pdf_path = MOCK_DIR / f"{name}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample file not found: {pdf_path}")

    total_pages = pdf_page_count(str(pdf_path)) if HAS_PDFIUM else 1
    contract = analyze_contract([str(pdf_path)])
    flags = evaluate(contract)
    return {"contract": contract, "flags": flags, "source_id": name, "total_pages": total_pages, "is_pdf": True}


@app.get("/api/page-image/{source_id}/{page_num}")
async def page_image(source_id: str, page_num: int):
    if source_id in VALID_SAMPLES:
        pdf_path = MOCK_DIR / f"{source_id}.pdf"
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="Sample PDF not found")
        if not HAS_PDFIUM:
            raise HTTPException(status_code=501, detail="pypdfium2 not installed")
        doc = pdfium.PdfDocument(str(pdf_path))
        if page_num < 1 or page_num > len(doc):
            doc.close()
            raise HTTPException(status_code=416, detail=f"Page {page_num} out of range (1–{len(doc)})")
        page = doc[page_num - 1]
        bitmap = page.render(scale=2)
        pil_image = bitmap.to_pil()
        doc.close()
        import io
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")

    # Upload source — find file by uuid prefix
    matches = list(UPLOAD_DIR.glob(f"{source_id}_*"))
    if not matches:
        raise HTTPException(status_code=404, detail="Upload not found")
    file_path = matches[0]

    if str(file_path).lower().endswith(".pdf"):
        if not HAS_PDFIUM:
            raise HTTPException(status_code=501, detail="pypdfium2 not installed")
        doc = pdfium.PdfDocument(str(file_path))
        if page_num < 1 or page_num > len(doc):
            doc.close()
            raise HTTPException(status_code=416, detail=f"Page {page_num} out of range (1–{len(doc)})")
        page = doc[page_num - 1]
        bitmap = page.render(scale=2)
        pil_image = bitmap.to_pil()
        doc.close()
        import io
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")
    else:
        if page_num != 1:
            raise HTTPException(status_code=416, detail="Image uploads only have page 1")
        with open(file_path, "rb") as f:
            content = f.read()
        suffix = file_path.suffix.lower()
        media_type = "image/jpeg" if suffix in (".jpg", ".jpeg") else f"image/{suffix.lstrip('.')}"
        return Response(content=content, media_type=media_type)
