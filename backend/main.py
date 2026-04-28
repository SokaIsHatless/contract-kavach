from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil, uuid, os
from pathlib import Path
from claude_vision import analyze_contract
from rules import evaluate

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/api/analyze")
async def analyze(files: list[UploadFile] = File(...)):
    paths = []
    for f in files:
        dest = UPLOAD_DIR / f"{uuid.uuid4()}_{f.filename}"
        with open(dest, "wb") as out:
            shutil.copyfileobj(f.file, out)
        paths.append(str(dest))
    contract = analyze_contract(paths)
    flags = evaluate(contract)
    for p in paths:
        os.remove(p)
    return {"contract": contract, "flags": flags}
