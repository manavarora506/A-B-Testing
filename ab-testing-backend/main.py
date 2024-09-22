import datetime
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from motor.motor_asyncio import AsyncIOMotorClient
import random
from typing import Dict, Any
import certifi

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables from the .env file
load_dotenv()

# Access the MongoDB URI from the environment variable
MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL, tls=True, tlsCAFile=certifi.where())
db = client['contact_form_db']
form_submissions_collection = db['form_submissions']
form_config_collection = db['form_config']

# Form configurations and metrics
form_config = {
    "fields": [
        {"type": "text", "label": "Full Name", "name": "full_name", "required": True},
        {"type": "email", "label": "Email", "name": "email", "required": True},
        {"type": "textarea", "label": "Message", "name": "message", "required": True}
    ],
    "styles": {
        "background_color": "#f0f8ff",
        "font_family": "Arial, sans-serif"
    },
    "images": []
}

routing_probability = 0.5
metrics = {
    "site_a_visits": 0,
    "site_b_visits": 0,
    "site_a_submissions": 0,
    "site_b_submissions": 0
}

class FormSubmission(BaseModel):
    full_name: str
    email: str
    message: str

    class Config:
        extra = 'allow'

class ProbabilityUpdate(BaseModel):
    probability: float

@app.get("/route")
async def route_user():
    if random.random() < routing_probability:
        metrics["site_a_visits"] += 1
        return {"site": "A"}
    else:
        metrics["site_b_visits"] += 1
        return {"site": "B"}

@app.get("/admin/form-config")
async def get_form_config():
    config = await form_config_collection.find_one({})
    if config:
        config['_id'] = str(config['_id'])
        config['routing_probability'] = config.get('routing_probability', routing_probability)
        return config 
    else:
        return {
            "fields": form_config['fields'],
            "styles": form_config['styles'],
            "images": form_config['images'],
            "routing_probability": routing_probability
        }

@app.put("/admin/save-form-config")
async def save_form_config(new_config: dict):
    global routing_probability
    try:
        routing_probability = new_config.pop('routing_probability', routing_probability)
        if '_id' in new_config:
            new_config.pop('_id')

        new_config['routing_probability'] = routing_probability
        result = await form_config_collection.update_one({}, {'$set': new_config}, upsert=True)
        
        if result.modified_count == 0 and result.upserted_id is None:
            raise HTTPException(status_code=400, detail="No changes made or document not found.")
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/admin/update-form")
async def update_form_config(new_config: dict):
    global form_config
    form_config = new_config
    return {"status": "success"}

@app.put("/admin/update-routing-probability")
async def update_routing_probability(update: ProbabilityUpdate):
    probability = update.probability
    global routing_probability
    if 0 <= probability <= 1:
        routing_probability = probability
        return {"status": "success"}
    else:
        raise HTTPException(status_code=400, detail="Probability must be between 0 and 1")

def validate_submission(data: Dict[str, Any], required_fields: Dict[str, bool]) -> None:
    """
    Validate the submission data based on required fields.
    """
    missing_fields = [field for field in required_fields if required_fields[field] and field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

@app.post("/submit-form/site-a")
async def submit_form_site_a(submission: FormSubmission):
    try:
        metrics["site_a_submissions"] += 1
        await form_submissions_collection.insert_one({
            "full_name": submission.full_name,
            "email": submission.email,
            "message": submission.message,
            "site": "A",
            "created_at": datetime.datetime.now()
        })
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-form/site-b")
async def submit_form_site_b(submission: Dict[str, Any]):
    try:
        # Fetch the current form configuration for Site B
        site_b_config = await form_config_collection.find_one({})
        site_b_fields = {field["name"] for field in site_b_config.get("fields", [])} if site_b_config else set()
        site_b_styles = site_b_config.get("styles", {}) if site_b_config else {}
        site_b_images = site_b_config.get("images", []) if site_b_config else []

        # Fetch a sample submission from Site A for comparison
        site_a_submission_sample = await form_submissions_collection.find_one({"site": "A"})

        # Compare fields between Site A and Site B
        if site_a_submission_sample:
            site_a_fields = set(site_a_submission_sample.keys())
            site_a_fields.discard("_id")
            site_a_fields.discard("site")
            site_a_fields.discard("created_at")
        else:
            site_a_fields = set()

        # Field differences
        field_diff = list(site_a_fields.symmetric_difference(site_b_fields))

        # Compare styles between Site A and Site B (assuming Site A default styles)
        site_a_styles = {
            "background_color": "#f0f8ff",
            "font_family": "Arial, sans-serif"
        }
        style_diff = {key: (site_a_styles.get(key), site_b_styles.get(key)) for key in set(site_a_styles) | set(site_b_styles)
                      if site_a_styles.get(key) != site_b_styles.get(key)}

        # Compare images (assuming no images in Site A by default)
        site_a_images = []
        image_diff = list(set(site_a_images).symmetric_difference(site_b_images))

        # Validate required fields based on Site B form config
        required_fields = {field["name"]: field.get("required", False) for field in site_b_config.get("fields", [])}
        validate_submission(submission, required_fields)

        # Track the submission
        metrics["site_b_submissions"] += 1

        # Save to MongoDB with the differences included
        await form_submissions_collection.insert_one({
            **submission,
            "site": "B",
            "created_at": datetime.datetime.utcnow(),
            "differences": {
                "field_differences": field_diff,
                "style_differences": style_diff,
                "image_differences": image_diff
            }
        })
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    difference_in_submissions = metrics["site_a_submissions"] - metrics["site_b_submissions"]
    
    return {
        "site_a_visits": metrics["site_a_visits"],
        "site_b_visits": metrics["site_b_visits"],
        "site_a_submissions": metrics["site_a_submissions"],
        "site_b_submissions": metrics["site_b_submissions"],
        "submission_difference": difference_in_submissions
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
