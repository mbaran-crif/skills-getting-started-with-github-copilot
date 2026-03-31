"""Tests for the High School Management System API"""

import pytest


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivities:
    """Tests for the activities endpoint"""

    def test_get_all_activities(self, client):
        """Test getting all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert len(activities) == 9

    def test_activity_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]

        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for activity signup endpoint"""

    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_email_to_participants(self, client):
        """Test that signup actually adds email to participants list"""
        email = "test.student@mergington.edu"
        client.post(f"/activities/Art Studio/signup?email={email}")

        # Verify the email was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Art Studio"]["participants"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_email(self, client):
        """Test signup with email already registered"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_missing_email_parameter(self, client):
        """Test signup without email parameter"""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Unprocessable Entity


class TestUnregister:
    """Tests for activity unregister endpoint"""

    def test_successful_unregister(self, client):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_email(self, client):
        """Test that unregister removes email from participants"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess Club/unregister?email={email}")

        # Verify email was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self, client):
        """Test unregister for student not in activity"""
        response = client.delete(
            "/activities/Tennis/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not found in activity"

    def test_unregister_missing_email_parameter(self, client):
        """Test unregister without email parameter"""
        response = client.delete("/activities/Chess Club/unregister")
        assert response.status_code == 422  # Unprocessable Entity