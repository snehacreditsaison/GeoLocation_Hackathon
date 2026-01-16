# FastAPI app + endpoints

from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks, HTTPException
import uuid, json
from .db import init_db, SessionLocal, Job
from .processing import process_job
from .utils import save_file
from .models import IngestResp, JobReport
import os

app = FastAPI()
init_db()

@app.post("/ingest", response_model=IngestResp)
async def ingest(background_tasks: BackgroundTasks,
                 gps_lat: float = Form(...),
                 gps_lng: float = Form(...),
                 size_sqft: float | None = Form(None),
                 photos: list[UploadFile] = File(...)):
    if len(photos) == 0 or len(photos) > 6:
        raise HTTPException(status_code=400, detail="Upload 1-6 photos")
    job_id = str(uuid.uuid4())
    paths = []
    for i, f in enumerate(photos):
        p = f"data/{job_id}/photo_{i}.jpg"
        content = await f.read()
        save_file(p, content)
        paths.append(p)
    # persist job
    db = SessionLocal()
    job = Job(id=job_id, status="pending", gps_lat=gps_lat, gps_lng=gps_lng, size_sqft=size_sqft, photos=json.dumps(paths))
    db.add(job); db.commit(); db.close()
    # background processing
    background_tasks.add_task(process_job, job_id, gps_lat, gps_lng, size_sqft, paths)
    return {"job_id": job_id, "status_url": f"/report/{job_id}"}

@app.get("/report/{job_id}", response_model=JobReport)
def get_report(job_id: str):
    db = SessionLocal()
    job = db.query(Job).get(job_id)
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.result:
        return json.loads(job.result)
    # return minimal in-progress response
    return {
        "job_id": job.id,
        "status": job.status,
        "gps_lat": job.gps_lat,
        "gps_lng": job.gps_lng,
        "size_sqft": job.size_sqft,
        "valuation_estimate": None,
        "health_score": None,
        "cv_labels": None,
        "nearest_pois": None,
        "risk_flags": None
    }
