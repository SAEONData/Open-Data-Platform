# format constraint for *_key fields
# ensures that we do not upset the CKAN-based metadata management system
KEY_REGEX = r'^[a-z0-9_\-]{2,100}$'


class Pagination:
    def __init__(self, offset: int = 0, limit: int = 100):
        self.offset = offset
        self.limit = limit
