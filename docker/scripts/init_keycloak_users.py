import time
import requests
from keycloak import KeycloakAdmin
from typing import Dict, List
import sys


def wait_for_keycloak(base_url: str, max_retries: int = 30, delay: int = 5) -> bool:
    """Wait for Keycloak to become available."""
    print(f"Waiting for Keycloak to start at {base_url}")
    for i in range(max_retries):
        try:
            # Check both master and ss-realm
            master_response = requests.get(f"{base_url}/realms/master")
            ss_response = requests.get(f"{base_url}/realms/ss-realm")
            if master_response.status_code in [
                200,
                401,
                403,
            ] and ss_response.status_code in [200, 401, 403]:
                print("Keycloak and ss-realm are available!")
                return True
        except requests.RequestException as e:
            print(
                f"Attempt {i + 1}/{max_retries}: Keycloak not ready yet. Error: {str(e)}"
            )
            time.sleep(delay)
    return False


def create_test_users(keycloak_admin: KeycloakAdmin) -> None:
    """Create test users in Keycloak."""
    test_users: List[Dict] = [
        {
            "username": "john",
            "email": "john@gmail.com",
            "firstName": "John",
            "lastName": "Smith",
            "enabled": True,
            "credentials": [{"type": "password", "value": "123", "temporary": False}],
        },
        {
            "username": "steve",
            "email": "steve@gmail.com",
            "firstName": "Steve",
            "lastName": "Jobs",
            "enabled": True,
            "credentials": [{"type": "password", "value": "123", "temporary": False}],
        },
    ]

    for user in test_users:
        try:
            existing_users = keycloak_admin.get_users(
                query={"username": user["username"]}
            )
            if not existing_users:
                keycloak_admin.create_user(payload=user)
                print(f"Created user: {user['username']}")
            else:
                print(f"User already exists: {user['username']}")
        except Exception as e:
            print(f"Error creating user {user['username']}: {e}")


def main():
    # Initial delay to ensure Keycloak is fully started
    initial_delay = 30
    print(f"Initial delay of {initial_delay} seconds to ensure Keycloak is ready...")
    time.sleep(initial_delay)

    server_url = "http://keycloak:8080"
    admin_username = "admin"
    admin_password = "admin"
    realm_name = "ss-realm"

    if not wait_for_keycloak(server_url):
        print("Keycloak is not available after maximum retries. Exiting...")
        sys.exit(1)

    try:
        print("Attempting to connect to Keycloak admin...")
        # Connect to master realm first
        keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            username=admin_username,
            password=admin_password,
            realm_name="master",
            verify=True,
        )

        # Get the ss-realm ID
        realms = keycloak_admin.get_realms()
        ss_realm_id = None
        for realm in realms:
            if realm["realm"] == "ss-realm":
                ss_realm_id = realm["id"]
                break

        if not ss_realm_id:
            print("ss-realm not found!")
            sys.exit(1)

        print(f"Found ss-realm with ID: {ss_realm_id}")

        # Create a new admin instance specifically for ss-realm
        keycloak_ss_admin = KeycloakAdmin(
            server_url=server_url,
            username=admin_username,
            password=admin_password,
            realm_name="ss-realm",
            user_realm_name="master",  # authenticate as admin in master realm
            verify=True,
        )

        print("Creating test users in ss-realm...")
        create_test_users(keycloak_ss_admin)
        print("Test users created successfully!")
        sys.exit(0)

    except Exception as e:
        print(f"Error initializing Keycloak admin client: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
