import html
import re
import unicodedata
from typing import List, Tuple


def sanitize_text(text: str) -> str:

    if not text:
        return ""

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
        "\u2022": "-",
        "\u00a9": "(c)",
        "\u00ae": "(R)",
        "\u2122": "(TM)",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = unicodedata.normalize(
        "NFKC",
        text
    )

    text = re.sub(
        r"[ \t]+\n",
        "\n",
        text
    )

    text = re.sub(
        r"\n{4,}",
        "\n\n\n",
        text
    )

    return text.strip()


def safe_filename(document_type: str) -> str:

    value = re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        document_type
    ).strip("_").lower()

    return value or "legal_document"


def split_sections(
    text: str
) -> List[Tuple[str, str]]:

    lines = [
        line.strip()
        for line in sanitize_text(text).splitlines()
    ]

    sections = []

    current_heading = "Document"
    current_body = []

    def flush():

        nonlocal current_body

        if current_body:

            body = "\n".join(
                current_body
            ).strip()

            if body:

                sections.append(
                    (
                        current_heading,
                        body
                    )
                )

        current_body = []

    for line in lines:

        if not line:
            continue

        normalized = re.sub(
            r"^[#\s]+",
            "",
            line
        )

        is_heading = (
            bool(
                re.match(
                    r"^(SECTION\s+)?\d+[\.\)]\s+\S+",
                    normalized,
                    re.I
                )
            )
            or normalized.upper()
            in {
                "AGREEMENT",
                "PARTIES",
                "RECITALS",
                "DEFINITIONS",
                "SCOPE",
                "PAYMENT",
                "COMPENSATION",
                "CONFIDENTIALITY",
                "TERM",
                "TERMINATION",
                "GOVERNING LAW",
                "SIGNATURES",
                "RESPONSIBILITIES",
                "OBLIGATIONS",
                "GENERAL PROVISIONS",
            }
        )

        if is_heading:

            flush()

            current_heading = normalized

        else:

            current_body.append(
                normalized
            )

    flush()

    return sections or [
        (
            "Document",
            sanitize_text(text)
        )
    ]


def terms_from_input(
    terms: str
) -> list[str]:

    return [
        item.strip()
        for item in terms.split(";")
        if item.strip()
    ]


def html_preview(
    text: str
) -> str:

    escaped = html.escape(
        sanitize_text(text)
    )

    paragraphs = []

    for block in escaped.split("\n\n"):

        block = block.replace(
            "\n",
            "<br>"
        )

        paragraphs.append(
            f"<p>{block}</p>"
        )

    return "".join(paragraphs)