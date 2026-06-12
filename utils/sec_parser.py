import re

from bs4 import BeautifulSoup


def extract_main_10k(
    filing_path: str
) -> str:

    with open(
        filing_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        content = f.read()

    documents = re.findall(
        r"<DOCUMENT>(.*?)</DOCUMENT>",
        content,
        re.DOTALL
    )

    for doc in documents:

        type_match = re.search(
            r"<TYPE>(.*?)\n",
            doc
        )

        if not type_match:
            continue

        document_type = (
            type_match.group(1)
            .strip()
            .upper()
        )

        if document_type == "10-K":

            text_match = re.search(
                r"<TEXT>(.*?)</TEXT>",
                doc,
                re.DOTALL
            )

            if not text_match:
                return ""

            html_content = (
                text_match.group(1)
            )

            soup = BeautifulSoup(
                html_content,
                "lxml"
            )

            clean_text = (
                soup.get_text(
                    separator=" ",
                    strip=True
                )
            )

            return clean_text

def load_raw_filing(
    filing_path: str
) -> str:

    with open(
        filing_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        return f.read()    

    return ""