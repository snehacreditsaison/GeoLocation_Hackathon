# # Pydantic request/response

# import torch
# import torchvision.transforms as T
# from PIL import Image
# import requests
# from geopy.distance import geodesic
# import json
# from .utils import save_file, json_dump
# from .db import SessionLocal, Job
# import os

# # load model once
# MODEL = None
# TRANSFORM = T.Compose([T.Resize((224,224)), T.ToTensor()])

# LABELS = ["building", "damaged", "extension", "other"]  # simple labels for demo

# def load_model():
#     global MODEL
#     if MODEL is None:
#         MODEL = torch.hub.load("pytorch/vision", "resnet18", pretrained=True)
#         MODEL.eval()

# def infer_image(path):
#     img = Image.open(path).convert("RGB")
#     t = TRANSFORM(img).unsqueeze(0)
#     with torch.no_grad():
#         out = MODEL(t)
#     # use top-1 ImageNet label as proxy; return filename as dummy label for hackathon
#     return os.path.basename(path)

# def query_osm_pois(lat, lng, radius_m=2000):
#     # Overpass simple query to find amenity nodes nearby (fallback to Nominatim if blocked)
#     try:
#         q = f'[out:json][timeout:25];(node(around:{radius_m},{lat},{lng})["amenity"];);out center 10;'
#         r = requests.post("https://overpass-api.de/api/interpreter", data=q, timeout=10)
#         data = r.json()
#         pois = []
#         for el in data.get("elements", [])[:5]:
#             pois.append({"type": el.get("tags", {}).get("amenity"), "name": el.get("tags", {}).get("name"), "lat": el.get("lat"), "lon": el.get("lon")})
#         return pois
#     except Exception:
#         return []

# def compute_valuation(size_sqft, market_rate=100):
#     if not size_sqft:
#         return None
#     return round(size_sqft * market_rate, 2)

# def process_job(job_id, gps_lat, gps_lng, size_sqft, photo_paths):
#     load_model()
#     labels = []
#     for p in photo_paths:
#         lbl = infer_image(p)
#         labels.append(lbl)
#     pois = query_osm_pois(gps_lat, gps_lng)
#     val = compute_valuation(size_sqft)
#     health = 0.6
#     risk_flags = []
#     # save result JSON
#     result = {
#         "job_id": job_id,
#         "status": "done",
#         "gps_lat": gps_lat,
#         "gps_lng": gps_lng,
#         "size_sqft": size_sqft,
#         "valuation_estimate": val,
#         "health_score": health,
#         "cv_labels": labels,
#         "nearest_pois": pois,
#         "risk_flags": risk_flags
#     }
#     json_dump(f"data/{job_id}/result.json", result)
#     # update DB
#     db = SessionLocal()
#     job = db.query(Job).get(job_id)
#     if job:
#         job.status = "done"
#         job.result = json.dumps(result)
#         db.add(job)
#         db.commit()
#     db.close()


from pydantic import BaseModel
from typing import List, Optional, Any

class IngestResp(BaseModel):
    job_id: str
    status_url: str

class POI(BaseModel):
    type: Optional[str]
    name: Optional[str]
    lat: Optional[float]
    lon: Optional[float]

class JobReport(BaseModel):
    job_id: str
    status: str
    gps_lat: float
    gps_lng: float
    size_sqft: Optional[float]
    valuation_estimate: Optional[float]
    health_score: Optional[float]
    cv_labels: Optional[List[str]]
    nearest_pois: Optional[List[POI]]
    risk_flags: Optional[List[str]]
    # allow extra fields if you add more later
    extra: Optional[Any] = None
