import re
from typing import TypedDict


class IdentifiedRisk(TypedDict):
    risk: str
    severity: str
    summary: str
    evidence: str


CHUNK_SEPARATOR = "===================="

RISK_CATEGORIES: dict[str, list[str]] = {
    "Supply Chain Risk": [
        "supply chain",
        "supply and manufacturing",
        "manufacturing chain",
        "contract manufacturer",
        "suppliers",
        "manufacture and deliver",
        "logistics",
        "component",
        "inventory",
    ],
    "Regulatory Risk": [
        "regulatory",
        "regulations",
        "compliance",
        "government investigations",
        "rules and requirements",
        "laws and regulations",
        "legal and regulatory",
        "mandatory age verification",
        "online safety",
    ],
    "Cybersecurity Risk": [
        "cybersecurity",
        "cyber security",
        "ransomware",
        "data security",
        "security attack",
        "cyber attack",
        "data breach",
        "privacy",
    ],
    "Macroeconomic Risk": [
        "macroeconomic",
        "economic conditions",
        "consumer spending",
        "inflation",
        "recession",
        "economic downturn",
        "interest rates",
        "exchange rates",
    ],
    "Geopolitical Risk": [
        "geopolitical",
        "political",
        "terrorist",
        "hostile acts",
        "international",
        "trade",
        "sanctions",
        "regions or countries",
    ],
    "Acquisition / Expansion Risk": [
        "acquisition",
        "acquisitions",
        "investments and acquisitions",
        "new business strategies",
        "commercial relationships",
        "new business",
        "write-offs",
        "impairment",
        "counterparty",
    ],
    "Litigation Risk": [
        "litigation",
        "lawsuit",
        "legal proceedings",
        "government investigations",
        "fines",
        "liability",
        "investigatory expenses",
    ],
    "Operational Risk": [
        "operational",
        "industrial accident",
        "fire",
        "power shortages",
        "labor disputes",
        "public health",
        "interruption",
        "disruption",
        "outages",
        "working environments",
    ],
}

SEVERITY_HIGH_TERMS = [
    "material adverse effect",
    "materially adversely",
    "material adverse impact",
    "significant write-offs",
    "impossible for the company",
    "serious injuries",
    "loss of life",
    "government investigations",
    "significant fees or fines",
]

SEVERITY_MEDIUM_TERMS = [
    "significant risks",
    "uncertainties",
    "may not be successful",
    "could delay",
    "could materially",
    "increase costs",
    "negatively impact",
    "subject to",
]

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

EXPLICIT_SECONDARY_ANCHORS: dict[str, list[str]] = {
    "Cybersecurity Risk": [
        "ransomware",
        "cybersecurity attack",
        "cyber attack",
        "data breach",
    ],
    "Supply Chain Risk": [
        "supply chain",
        "supply and manufacturing",
        "contract manufacturer",
    ],
    "Litigation Risk": [
        "litigation",
        "lawsuit",
        "legal proceedings",
    ],
    "Geopolitical Risk": [
        "terrorist",
        "hostile acts",
        "geopolitical",
        "sanctions",
    ],
}


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _strip_metadata(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Company:"):
            continue
        if stripped.startswith("Source:"):
            continue
        if not stripped:
            continue
        lines.append(stripped)

    return _normalize_whitespace(" ".join(lines))


def parse_retrieved_chunks(
    retrieved_context: str | None,
) -> list[str]:
    if not retrieved_context or not retrieved_context.strip():
        return []

    raw_chunks = retrieved_context.split(CHUNK_SEPARATOR)
    chunks = []

    for raw_chunk in raw_chunks:
        cleaned = _strip_metadata(raw_chunk)
        if len(cleaned) >= 80:
            chunks.append(cleaned)

    return chunks


def _count_keyword_matches(
    text: str,
    keywords: list[str],
) -> int:
    lowered = text.lower()
    return sum(
        1 for keyword in keywords if keyword in lowered
    )


def _is_boilerplate_chunk(chunk: str) -> bool:
    lowered = chunk.lower()

    if (
        "item 1a" in lowered
        and "the following summarizes" in lowered
    ):
        return True

    if (
        "form 10-k" in lowered
        and "risk factors" in lowered
        and "material adverse effect" in lowered
    ):
        return True

    return False


def classify_chunk_primary(
    chunk: str,
) -> str | None:
    if _is_boilerplate_chunk(chunk):
        return None

    scores = {
        category: _count_keyword_matches(chunk, keywords)
        for category, keywords in RISK_CATEGORIES.items()
    }

    best_score = max(scores.values())
    if best_score == 0:
        return None

    return sorted(
        category
        for category, score in scores.items()
        if score >= best_score
    )[0]


def _extract_anchor_excerpt(
    chunk: str,
    anchor: str,
    window: int = 220,
) -> str:
    lowered = chunk.lower()
    anchor_lower = anchor.lower()
    index = lowered.find(anchor_lower)

    if index == -1:
        return chunk

    start = max(0, index - 90)
    end = min(len(chunk), index + window)
    excerpt = chunk[start:end].strip()

    if start > 0:
        excerpt = "..." + excerpt
    if end < len(chunk):
        excerpt = excerpt + "..."

    return _normalize_whitespace(excerpt)


def _find_secondary_risk_excerpts(
    chunk: str,
    primary_category: str | None,
) -> list[tuple[str, str]]:
    lowered = chunk.lower()
    excerpts: list[tuple[str, str]] = []

    for category, anchors in EXPLICIT_SECONDARY_ANCHORS.items():
        if category == primary_category:
            continue

        for anchor in anchors:
            if anchor in lowered:
                excerpts.append(
                    (
                        category,
                        _extract_anchor_excerpt(
                            chunk,
                            anchor,
                        ),
                    )
                )
                break

    return excerpts


def score_severity(text: str) -> str:
    lowered = text.lower()

    high_matches = sum(
        1 for term in SEVERITY_HIGH_TERMS if term in lowered
    )
    medium_matches = sum(
        1 for term in SEVERITY_MEDIUM_TERMS if term in lowered
    )

    if high_matches >= 2 or (
        high_matches >= 1 and medium_matches >= 1
    ):
        return "HIGH"

    if high_matches >= 1 or medium_matches >= 2:
        return "MEDIUM"

    if medium_matches >= 1:
        return "LOW"

    return "MEDIUM"


def _merge_severity(
    current: str,
    incoming: str,
) -> str:
    return (
        current
        if SEVERITY_ORDER[current]
        <= SEVERITY_ORDER[incoming]
        else incoming
    )


def _is_usable_sentence(sentence: str) -> bool:
    sentence = sentence.strip()
    if len(sentence) < 50:
        return False

    if re.match(r"^[a-z]{1,3}[.|]\s", sentence):
        return False

    lowered = sentence.lower()
    if "form 10-k" in lowered and "item 1a" in lowered:
        return False

    return bool(re.match(r"[A-Z0-9\"(]", sentence))


def _first_sentences(
    text: str,
    max_chars: int = 280,
) -> str:
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    summary_parts = []
    total_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not _is_usable_sentence(sentence):
            continue

        if total_length + len(sentence) > max_chars:
            break

        summary_parts.append(sentence)
        total_length += len(sentence) + 1

        if len(summary_parts) >= 2:
            break

    if summary_parts:
        return " ".join(summary_parts)

    trimmed = text[:max_chars].strip()
    capital_match = re.search(r"[A-Z][^.!?]{40,}[.!?]", text)
    if capital_match:
        return capital_match.group(0)

    return trimmed + ("..." if len(text) > max_chars else "")


def _truncate_evidence(
    text: str,
    max_chars: int = 360,
) -> str:
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars].rstrip()
    last_space = truncated.rfind(" ")

    if last_space > max_chars // 2:
        truncated = truncated[:last_space]

    return truncated + "..."


def extract_identified_risks(
    retrieved_context: str | None,
) -> list[IdentifiedRisk]:
    grouped_text: dict[str, list[str]] = {}

    for chunk in parse_retrieved_chunks(retrieved_context):
        primary_category = classify_chunk_primary(chunk)

        if primary_category:
            grouped_text.setdefault(
                primary_category,
                [],
            ).append(chunk)

        secondary_excerpts = _find_secondary_risk_excerpts(
            chunk,
            primary_category,
        )

        for category, excerpt in secondary_excerpts:
            grouped_text.setdefault(
                category,
                [],
            ).append(excerpt)

    identified_risks: list[IdentifiedRisk] = []

    for category, texts in grouped_text.items():
        combined_text = " ".join(texts)
        best_text = max(
            texts,
            key=lambda text: _count_keyword_matches(
                text,
                RISK_CATEGORIES[category],
            ),
        )

        identified_risks.append(
            {
                "risk": category,
                "severity": score_severity(combined_text),
                "summary": _first_sentences(best_text),
                "evidence": _truncate_evidence(best_text),
            }
        )

    identified_risks.sort(
        key=lambda item: (
            SEVERITY_ORDER.get(item["severity"], 99),
            item["risk"],
        )
    )

    return identified_risks


def format_identified_risks(
    identified_risks: list[IdentifiedRisk],
) -> str:
    if not identified_risks:
        return (
            "No structured business risks could be identified from "
            "retrieved SEC context."
        )

    blocks = []

    for index, item in enumerate(identified_risks, start=1):
        blocks.append(
            f"{index}. {item['risk']} ({item['severity']})\n"
            f"   Summary:\n"
            f"   {item['summary']}\n\n"
            f"   Evidence:\n"
            f"   {item['evidence']}"
        )

    return "\n\n".join(blocks)
