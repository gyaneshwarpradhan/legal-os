"""Document classification service identifying legal document types and metadata."""
import re
from typing import Tuple


CLASSIFICATION_PATTERNS = {
    "complaint": [
        r"\bcomplaint\b",
        r"\bplaintiff\s+alleges\b",
        r"\bprayer\s+for\s+relief\b",
        r"\bjury\s+trial\s+demanded\b",
        r"\bcauses?\s+of\s+action\b",
    ],
    "answer": [
        r"\banswer\s+to\b",
        r"\baffirmative\s+defenses\b",
        r"\bdefendant\s+answers\b",
        r"\bgeneral\s+denial\b",
    ],
    "motion": [
        r"\bmotion\s+to\s+compel\b",
        r"\bmotion\s+for\s+summary\s+judgment\b",
        r"\bnotice\s+of\s+motion\b",
        r"\bmemorandum\s+of\s+points\s+and\s+authorities\b",
    ],
    "discovery_request": [
        r"\bfirst\s+set\s+of\s+interrogatories\b",
        r"\brequest\s+for\s+production\s+of\s+documents\b",
        r"\brequests?\s+for\s+admission\b",
        r"\binterrogator(y|ies)\b",
    ],
    "discovery_response": [
        r"\bresponses?\s+to\s+(first\s+set\s+of\s+)?interrogatories\b",
        r"\bresponse\s+to\s+request\s+for\s+production\b",
        r"\bresponses?\s+and\s+objections\b",
    ],
    "deposition": [
        r"\bdeposition\s+of\b",
        r"\bvideotaped\s+deposition\b",
        r"\bexamination\s+by\s+(mr\.|ms\.)\b",
        r"\bcertificate\s+of\s+reporter\b",
    ],
    "medical_record": [
        r"\bpatient\s+name\b",
        r"\bchief\s+complaint\b",
        r"\bdiagnos(is|es)\b",
        r"\btreatment\s+plan\b",
        r"\bphysician\b",
        r"\bhistory\s+of\s+present\s+illness\b",
    ],
    "expert_report": [
        r"\bexpert\s+(witness\s+)?report\b",
        r"\bopinions\s+to\s+a\s+reasonable\s+degree\b",
        r"\bcurriculum\s+vitae\b",
        r"\bretained\s+by\s+counsel\b",
    ],
    "court_order": [
        r"\bit\s+is\s+(hereby\s+)?ordered\b",
        r"\border\s+granting\b",
        r"\border\s+denying\b",
        r"\bso\s+ordered\b",
        r"\bjudge\s+of\s+the\s+superior\s+court\b",
    ],
    "correspondence": [
        r"\bdear\s+(mr\.|ms\.|counsel)\b",
        r"\bsincerely\b",
        r"\bvia\s+(electronic\s+mail|email|facsimile)\b",
    ],
}


def classify_document(file_name: str, text: str) -> Tuple[str, float, str]:
    """
    Classify legal document based on content heuristics and file name cues.
    Returns (predicted_type, confidence_score, candidate_title).
    """
    normalized_text = (text[:10000] if text else "").lower()
    normalized_fname = file_name.lower()

    scores = {}
    for doc_type, patterns in CLASSIFICATION_PATTERNS.items():
        score = 0
        for pat in patterns:
            if re.search(pat, normalized_text):
                score += 2
            if re.search(pat, normalized_fname):
                score += 3
        if score > 0:
            scores[doc_type] = score

    if not scores:
        candidate_title = Path_clean_title(file_name)
        return "other", 0.5, candidate_title

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    confidence = min(0.99, max(0.65, 0.5 + (best_score * 0.08)))

    candidate_title = extract_title(text, file_name, best_type)
    return best_type, round(confidence, 2), candidate_title


def extract_title(text: str, file_name: str, doc_type: str) -> str:
    """Extract a representative clean title from the document header or filename."""
    lines = [l.strip() for l in text[:2000].split("\n") if len(l.strip()) > 5]
    for line in lines[:8]:
        # Filter out numbers, court headers or dates
        if not re.match(r"^(\d+|date|superior|court|county|state)", line.lower()):
            if 10 < len(line) < 120:
                return line

    return Path_clean_title(file_name)


def Path_clean_title(file_name: str) -> str:
    from pathlib import Path

    stem = Path(file_name).stem
    clean = re.sub(r"[_-]+", " ", stem)
    return clean.title()
