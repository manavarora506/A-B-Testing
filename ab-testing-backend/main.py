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

# Enable Cross-Origin Resource Sharing (CORS) to allow the frontend (React) to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Load environment variables from the .env file
load_dotenv()

# Access the MongoDB URI from the environment variable
MONGO_URL = os.getenv("MONGO_URL")

# Establish a connection to the MongoDB database using Motor (async driver) with TLS for security
client = AsyncIOMotorClient(MONGO_URL, tls=True, tlsCAFile=certifi.where())
db = client['contact_form_db']  # Use a database named 'contact_form_db'
form_submissions_collection = db['form_submissions']  # Collection for form submissions
form_config_collection = db['form_config']  # Collection for form configurations

# Default form configurations and metrics (could also be stored in the database)
form_config = {
    "fields": [
        {"type": "text", "label": "Full Name", "name": "full_name", "required": True},
        {"type": "email", "label": "Email", "name": "email", "required": True},
        {"type": "textarea", "label": "Message", "name": "message", "required": True}
    ],
    "styles": {
        "background_color": "#f0f8ff",  # Default background color
        "font_family": "Arial, sans-serif"  # Default font family
    },
    "images": []  # List to store any images in the form (currently empty)
}

# Default routing probability (50% chance to route to Site A or Site B)
routing_probability = 0.5

# Metrics to track visits and submissions for both Site A and Site B
metrics = {
    "site_a_visits": 0,
    "site_b_visits": 0,
    "site_a_submissions": 0,
    "site_b_submissions": 0
}

# Pydantic model to validate form submissions for Site A
class FormSubmission(BaseModel):
    full_name: str
    email: str
    message: str

    class Config:
        extra = 'allow'  # Allow extra fields not defined in the model

# Pydantic model to validate updates to the routing probability
class ProbabilityUpdate(BaseModel):
    probability: float

# Endpoint to route users to either Site A or Site B based on routing probability
@app.get("/route")
async def route_user():
    if random.random() < routing_probability:  # Route based on probability
        metrics["site_a_visits"] += 1  # Track visit to Site A
        return {"site": "A"}
    else:
        metrics["site_b_visits"] += 1  # Track visit to Site B
        return {"site": "B"}

# Admin endpoint to retrieve the current form configuration (for Site B)
@app.get("/admin/form-config")
async def get_form_config():
    config = await form_config_collection.find_one({})
    if config:
        # Convert MongoDB ObjectId to string for JSON compatibility
        config['_id'] = str(config['_id'])
        config['routing_probability'] = config.get('routing_probability', routing_probability)
        return config
    else:
        # If no config in the database, return the default form config
        return {
            "fields": form_config['fields'],
            "styles": form_config['styles'],
            "images": form_config['images'],
            "routing_probability": routing_probability
        }

# Admin endpoint to save the updated form configuration (for Site B)
@app.put("/admin/save-form-config")
async def save_form_config(new_config: dict):
    global routing_probability
    try:
        # Extract routing probability from the config and update the global value
        routing_probability = new_config.pop('routing_probability', routing_probability)
        
        # Remove MongoDB '_id' field if present
        if '_id' in new_config:
            new_config.pop('_id')

        # Update form configuration in the database with new values
        new_config['routing_probability'] = routing_probability
        result = await form_config_collection.update_one({}, {'$set': new_config}, upsert=True)

        # Check if the document was updated or inserted, if not, raise an exception
        if result.modified_count == 0 and result.upserted_id is None:
            raise HTTPException(status_code=400, detail="No changes made or document not found.")
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin endpoint to update the current form configuration in-memory
@app.put("/admin/update-form")
async def update_form_config(new_config: dict):
    global form_config
    form_config = new_config  # Update the global form configuration
    return {"status": "success"}

# Admin endpoint to update the routing probability between Site A and Site B
@app.put("/admin/update-routing-probability")
async def update_routing_probability(update: ProbabilityUpdate):
    probability = update.probability
    global routing_probability
    if 0 <= probability <= 1:
        routing_probability = probability  # Update the global routing probability
        return {"status": "success"}
    else:
        # Return an error if the probability is outside of [0, 1]
        raise HTTPException(status_code=400, detail="Probability must be between 0 and 1")

# Helper function to validate submission data based on required fields from the form config
def validate_submission(data: Dict[str, Any], required_fields: Dict[str, bool]) -> None:
    """
    Validate the submission data based on required fields.
    """
    missing_fields = [field for field in required_fields if required_fields[field] and field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

# Endpoint to submit the form for Site A
@app.post("/submit-form/site-a")
async def submit_form_site_a(submission: FormSubmission):
    try:
        # Increment Site A submission metrics
        metrics["site_a_submissions"] += 1
        # Insert the submission into MongoDB with a timestamp
        await form_submissions_collection.insert_one({
            "full_name": submission.full_name,
            "email": submission.email,
            "message": submission.message,
            "site": "A",
            "created_at": datetime.datetime.now()  # Record the submission time
        })
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to submit the form for Site B (with configuration and comparison)
@app.post("/submit-form/site-b")
async def submit_form_site_b(submission: Dict[str, Any]):
    try:
        # Fetch the current form configuration for Site B from the database
        site_b_config = await form_config_collection.find_one({})
        site_b_fields = {field["name"] for field in site_b_config.get("fields", [])} if site_b_config else set()
        site_b_styles = site_b_config.get("styles", {}) if site_b_config else {}
        site_b_images = site_b_config.get("images", []) if site_b_config else []

        # Fetch a sample submission from Site A for comparison
        site_a_submission_sample = await form_submissions_collection.find_one({"site": "A"})

        # Compare fields between Site A and Site B
        if site_a_submission_sample:
            site_a_fields = set(site_a_submission_sample.keys())
            site_a_fields.discard("_id")  # Exclude MongoDB ObjectId
            site_a_fields.discard("site")  # Exclude the site field
            site_a_fields.discard("created_at")  # Exclude the timestamp
        else:
            site_a_fields = set()

        # Compute differences between Site A and Site B fields
        field_diff = list(site_a_fields.symmetric_difference(site_b_fields))

        # Compare styles between Site A and Site B (using default Site A styles)
        site_a_styles = {
            "background_color": "#f0f8ff",
            "font_family": "Arial, sans-serif"
        }
        style_diff = {key: (site_a_styles.get(key), site_b_styles.get(key)) for key in set(site_a_styles) | set(site_b_styles)
                      if site_a_styles.get(key) != site_b_styles.get(key)}

        # Compare images (assuming no images in Site A by default)
        site_a_images = []
        image_diff = list(set(site_a_images).symmetric_difference(site_b_images))

        # Validate the form submission for Site B based on required fields
        required_fields = {field["name"]: field.get("required", False) for field in site_b_config.get("fields", [])}
        validate_submission(submission, required_fields)

        # Increment Site B submission metrics
        metrics["site_b_submissions"] += 1

        # Save the submission to MongoDB with the differences in fields, styles, and images
        await form_submissions_collection.insert_one({
            **submission,
            "site": "B",
            "created_at": datetime.datetime.now(),  # Record the submission time
            "field_diff": field_diff,  # Log field differences
            "style_diff": style_diff,  # Log style differences
            "image_diff": image_diff  # Log image differences
        })
        return {"status": "success", "field_diff": field_diff, "style_diff": style_diff, "image_diff": image_diff}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin endpoint to view the metrics for Site A and Site B
@app.get("/admin/metrics")
async def get_metrics():
    return metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
