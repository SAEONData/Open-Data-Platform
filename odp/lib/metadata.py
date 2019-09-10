DOI_REGEX = r'^10\.\d+(\.\d+)*/.+$'


class MetadataRecordsFilter:
    def __init__(self, institution: str = None, infrastructure: str = None):
        self.institution = institution
        self.infrastructure = infrastructure
