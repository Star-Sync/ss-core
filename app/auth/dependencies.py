from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError
from typing import List, Dict
from .keycloak import keycloak_service

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="http://localhost:8080/realms/ss-realm/protocol/openid-connect/auth",
    tokenUrl="http://localhost:8080/realms/ss-realm/protocol/openid-connect/token",
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        return await keycloak_service.verify_token(token)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(required_roles: List[str]):
    async def role_checker(current_user: Dict = Depends(get_current_user)):
        if "realm_access" not in current_user:
            raise HTTPException(status_code=403, detail="No roles available")

        user_roles = current_user["realm_access"]["roles"]
        for role in required_roles:
            if role not in user_roles:
                raise HTTPException(status_code=403, detail=f"Role {role} is required")
        return current_user

    return role_checker
