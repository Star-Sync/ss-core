# # test_auth.py
# import pytest
# from fastapi.testclient import TestClient

# # Adjust this import according to your project structure!
# from app.main import app

# client = TestClient(app)


# def test_register_user():
#     """
#     Test proper registration of a new user.
#     """
#     user_data = {
#         "username": "testuser",
#         "email": "testuser@example.com",
#         "password": "secretpassword"
#     }
#     response = client.post("/api/v1/auth/register", json=user_data)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     # Check that username and email are returned, but not the hashed password.
#     assert data["username"] == user_data["username"]
#     assert data["email"] == user_data["email"]


# def test_duplicate_registration():
#     """
#     Test that duplicate username or email registration fails.
#     """
#     user_data = {
#         "username": "dupuser",
#         "email": "dupuser@example.com",
#         "password": "secret123"
#     }
#     # First registration should succeed.
#     response = client.post("/api/v1/auth/register", json=user_data)
#     assert response.status_code == 200, response.text

#     # Second registration with the same username should fail.
#     response = client.post("/api/v1/auth/register", json=user_data)
#     assert response.status_code == 400, response.text
#     assert "already registered" in response.json()["detail"]


# def test_login_and_access_me():
#     """
#     Test user login to get token and then retrieving the user profile.
#     """
#     # First, create a new user for testing.
#     user_data = {
#         "username": "loginuser",
#         "email": "loginuser@example.com",
#         "password": "mypassword"
#     }
#     response = client.post("/api/v1/auth/register", json=user_data)
#     assert response.status_code == 200, response.text

#     # Now, try logging in using OAuth2PasswordRequestForm data.
#     login_data = {
#         "username": "loginuser",
#         "password": "mypassword"
#     }
#     # Note: The login endpoint expects form-data, so pass the data as `data` not `json`.
#     response = client.post("/api/v1/auth/token", data=login_data)
#     assert response.status_code == 200, response.text

#     token_data = response.json()
#     assert "access_token" in token_data
#     access_token = token_data["access_token"]

#     # Use the token to access the user's own profile.
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = client.get("/api/v1/auth/users/me", headers=headers)
#     assert response.status_code == 200, response.text

#     user_info = response.json()
#     assert user_info["username"] == "loginuser"
#     assert user_info["email"] == "loginuser@example.com"


# def test_invalid_login():
#     """
#     Test that login fails with wrong credentials.
#     """
#     login_data = {"username": "nonexistent", "password": "wrongpassword"}
#     response = client.post("/api/v1/auth/token", data=login_data)
#     assert response.status_code == 401, response.text
#     assert "Incorrect username or password" in response.json()["detail"]


# def test_inactive_user_access(tmp_path):
#     """
#     (Optional) If your User model uses an 'is_active' flag to deactivate users,
#     you can test that inactive users cannot access the /users/me endpoint.

#     This test assumes that you have a way of updating the user's 'is_active' property.
#     """
#     # Register and login a new user.
#     user_data = {
#         "username": "inactiveuser",
#         "email": "inactive@example.com",
#         "password": "securepass"
#     }
#     response = client.post("/api/v1/auth/register", json=user_data)
#     assert response.status_code == 200, response.text

#     login_data = {"username": "inactiveuser", "password": "securepass"}
#     response = client.post("/api/v1/auth/token", data=login_data)
#     assert response.status_code == 200, response.text
#     token = response.json()["access_token"]

#     # Here we simulate marking user as inactive.
#     # In a real test, you could override the dependency that provides the database session,
#     # then update the user's "is_active" flag directly.
#     # For this example, assume your app has a test endpoint to deactivate the user.
#     # (If not, you could use your session to update the record.)
#     #
#     # For demonstration:
#     # client.post("/api/v1/auth/deactivate", json={"username": "inactiveuser"})

#     # Assuming the user is now inactive, accessing /users/me should result in a 400.
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("/api/v1/auth/users/me", headers=headers)
#     # Adjust the expected status code/message if your implementation differs.
#     assert response.status_code == 400, response.text
#     assert "Inactive user" in response.json()["detail"]
