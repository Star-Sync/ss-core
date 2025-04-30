import logging
from typing import List, Optional
from fastapi import HTTPException
from enum import Enum
from app.models.user import UserModel

logger = logging.getLogger(__name__)


class Action(Enum):
    READ = "read"
    WRITE = "write"


PERMISSIONS = {
    "SYS_ADMIN": {Action.READ, Action.WRITE},
    "SYS_USER": {Action.READ},
    "MISSION_ADMIN": {Action.READ, Action.WRITE},
    "MISSION_USER": {Action.READ},
}


def check_action(user: UserModel, action: Action) -> None:
    if action not in PERMISSIONS[user.role]:
        logger.exception(
            f"User ID:{user.id} with '{user.role}' role lacks permission to {action.value} resource"
        )
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions",
        )


def check_mission_access(user: UserModel, resource_mission: str):
    # Mission-specific check
    user_mission_access = user.mission_access

    if user.role in ["MISSION_ADMIN", "MISSION_USER"]:
        if not user_mission_access:
            logger.exception(
                f"User ID: {user.id} with '{user.role}' role has no approved missions to access"
            )
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        if resource_mission not in user_mission_access:
            logger.exception(
                f"Mission '{resource_mission}' not part of approved missions {user_mission_access} for user ID:{user.id} with role '{user.role}'"
            )
            raise HTTPException(
                status_code=403,
                detail=f"No access to mission '{resource_mission}'",
            )


def has_system_privileges(user: UserModel) -> bool:
    return user.role in ["SYS_ADMIN", "SYS_USER"]


def is_sys_admin(user: UserModel) -> bool:
    return user.role == "SYS_ADMIN"
