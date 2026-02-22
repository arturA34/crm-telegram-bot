from enum import StrEnum


class UserRole(StrEnum):
    SOLO = "SOLO"
    OWNER = "OWNER"
    MANAGER = "MANAGER"


class ClientStatus(StrEnum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    PROPOSAL_SENT = "PROPOSAL_SENT"
    WON = "WON"
    LOST = "LOST"
