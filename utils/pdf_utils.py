from pypdf import PdfReader


def extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def extract_financial_context(text: str) -> str:
    sections = []

    statement_headers = [
    "CONSOLIDATED STATEMENTS OF OPERATIONS",
    "CONSOLIDATED BALANCE SHEETS",
    "CONSOLIDATED STATEMENTS OF CASH FLOWS"
]

    upper_text = text.upper()

    for header in statement_headers:
        idx = upper_text.find(header)

        if idx != -1:
            start = idx
            end = min(len(text), idx + 6000)

            sections.append(text[start:end])

    return "\n\n".join(sections)