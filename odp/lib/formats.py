# adapted from https://www.crossref.org/blog/dois-and-matching-regular-expressions
DOI_REGEX = r'^10\.\d{4,}(\.\d+)*/[-._;()/:a-zA-Z0-9]+$'

# the suffix part of the DOI regex suffices for secondary IDs
SID_REGEX = r'^[-._;()/:a-zA-Z0-9]+$'
