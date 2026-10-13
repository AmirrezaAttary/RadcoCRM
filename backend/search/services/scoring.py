from .normalizer import SearchNormalizer


def calculate_match_score(
    query,
    title=None,
    description=None,
    extra_fields=None,
):
    query = SearchNormalizer.normalize(query)

    if not query:
        return 0.0

    title = SearchNormalizer.normalize(title)
    description = SearchNormalizer.normalize(description)

    extra_fields = extra_fields or []

    if title == query:
        return 1.00

    if title.startswith(query):
        return 0.90

    if query in title:
        return 0.75

    if description:
        if description == query:
            return 0.70

        if description.startswith(query):
            return 0.60

        if query in description:
            return 0.50

    for field in extra_fields:
        field = SearchNormalizer.normalize(field)

        if not field:
            continue

        if field == query:
            return 0.65

        if field.startswith(query):
            return 0.55

        if query in field:
            return 0.45

    return 0.0