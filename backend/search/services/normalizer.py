import re


class SearchNormalizer:

    CHAR_REPLACEMENTS = str.maketrans({
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "ٱ": "ا",
    })

    @classmethod
    def normalize(cls, value: str) -> str:
        if not value:
            return ""

        value = str(value)

        value = value.translate(cls.CHAR_REPLACEMENTS)

        value = re.sub(
            r"[\u064B-\u065F\u0670]",
            "",
            value,
        )

        value = re.sub(
            r"[\u00A0\u2000-\u200B\u202F\u205F]",
            " ",
            value,
        )

        value = value.replace("\u200c", " ")

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()