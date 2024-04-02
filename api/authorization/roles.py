from api.constants import READ_DATA_PERMISSION, VIEW_DATA_INVALIDATION_REASONS_PERMISSION

ROLES = {
    "admin": [READ_DATA_PERMISSION, VIEW_DATA_INVALIDATION_REASONS_PERMISSION],
    "user": [READ_DATA_PERMISSION]
}