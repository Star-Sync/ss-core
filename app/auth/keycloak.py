from keycloak import KeycloakOpenID
from fastapi import HTTPException, status
from typing import Dict


class KeycloakService:
    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url="http://localhost:8080/",
            client_id="ss-frontend",
            realm_name="ss-realm",
            client_secret_key=None,
        )
        self.public_key = self._get_public_key()

    def _get_public_key(self) -> str:
        try:
            return f"-----BEGIN PUBLIC KEY-----\n{self.keycloak_openid.public_key()}\n-----END PUBLIC KEY-----"
        except Exception as e:
            print(f"Error fetching public key: {e}")
            return ""

    async def verify_token(self, token: str) -> Dict:
        try:
            return self.keycloak_openid.decode_token(
                token,
                key=self.public_key,
                options={
                    "verify_signature": True,
                    "verify_aud": False,
                    "verify_exp": True,
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


keycloak_service = KeycloakService()
