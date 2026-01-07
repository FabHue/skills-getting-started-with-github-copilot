"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "Soccer Team": {
            "description": "Outdoor team sport focusing on skills and matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball practices and games",
            "schedule": "Tuesdays and Fridays, 5:00 PM - 7:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["mia@mergington.edu", "amelia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and school theater productions",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 30,
            "participants": ["charlotte@mergington.edu", "sophia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Practice argumentation, public speaking, and competitions",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "lucas@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Prepare for regional science competitions with hands-on projects",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["oliver@mergington.edu", "elijah@mergington.edu"]
        },
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    # Try to locate the activity (supports grouped activities like "Gym Class - Soccer Team")
    def _find_activity(name: str):
        if name in activities and isinstance(activities[name], dict) and "participants" in activities[name]:
            return activities[name]
        # search grouped activities
        for group_name, group_val in activities.items():
            if isinstance(group_val, dict):
                for sub_name, sub_val in group_val.items():
                    if sub_name == name or f"{group_name} - {sub_name}" == name:
                        return sub_val
        return None

    activity = _find_activity(activity_name)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.post("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    def _find_activity(name: str):
        if name in activities and isinstance(activities[name], dict) and "participants" in activities[name]:
            return activities[name]
        for group_name, group_val in activities.items():
            if isinstance(group_val, dict):
                for sub_name, sub_val in group_val.items():
                    if sub_name == name or f"{group_name} - {sub_name}" == name:
                        return sub_val
        return None

    activity = _find_activity(activity_name)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    if email not in activity.get("participants", []):
        raise HTTPException(status_code=404, detail="Student not registered for this activity")

    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
