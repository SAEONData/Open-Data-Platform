# adapted from https://www.crossref.org/blog/dois-and-matching-regular-expressions
DOI_REGEX = r'^10\.\d{4,}(\.\d+)*/[-._;()/:a-zA-Z0-9]+$'


class MetadataRecordsFilter:
    def __init__(self, institution: str = None, infrastructure: str = None):
        self.institution = institution
        self.infrastructure = infrastructure
