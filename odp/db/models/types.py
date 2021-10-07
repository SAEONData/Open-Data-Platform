from enum import Enum


class RoleType(str, Enum):
    PLATFORM = 'PLATFORM'
    CLIENT = 'CLIENT'
    PROJECT = 'PROJECT'
    PROVIDER = 'PROVIDER'
