from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # basic sanity: known keys exist
    assert "Chess Club" in data


def test_signup_and_unregister_flat_activity():
    activity = "Chess Club"
    email = "testuser@example.com"
    # ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    res = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert res.status_code == 200
    assert email in activities[activity]["participants"]

    # unregister
    res2 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert res2.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_and_unregister_grouped_activity():
    # e.g., "Gym Class - Soccer Team"
    activity = "Gym Class - Soccer Team"
    # find the activity dict from the app data
    # ensure not present
    # locate activity participants list
    # first ensure the activity exists
    res = client.get("/activities")
    data = res.json()
    assert "Gym Class" in data
    # perform signup
    email = "groupuser@example.com"
    # clean up pre-existing if present
    for group_name, group_val in activities.items():
        if group_name == "Gym Class":
            if isinstance(group_val, dict):
                for sub_name, sub_val in group_val.items():
                    if sub_name == "Soccer Team":
                        if email in sub_val["participants"]:
                            sub_val["participants"].remove(email)

    # perform signup via endpoint
    res = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert res.status_code == 200

    # verify internal state
    # find the participants list
    found = False
    for group_name, group_val in activities.items():
        if group_name == "Gym Class":
            if isinstance(group_val, dict):
                for sub_name, sub_val in group_val.items():
                    if sub_name == "Soccer Team":
                        assert email in sub_val["participants"]
                        found = True
    assert found

    # unregister
    res2 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert res2.status_code == 200

    # verify removed
    for group_name, group_val in activities.items():
        if group_name == "Gym Class":
            if isinstance(group_val, dict):
                for sub_name, sub_val in group_val.items():
                    if sub_name == "Soccer Team":
                        assert email not in sub_val["participants"]

