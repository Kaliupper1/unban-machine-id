"""Phone number validation and normalization for Egyptian numbers.

Validates input against Egyptian phone number patterns and returns
E.164 normalized format (+20XXXXXXXXX).
"""

import re

# Egyptian numbers: country code 20, then 9-10 digits.
# Mobile prefixes: 10, 11, 12, 15 (all 10-digit after country code).
# Landline: 2 (Cairo), 3 (Alexandria), etc. — typically 9 digits after CC.
_EGYPT_E164_RE = re.compile(r"^\+20\d{9,10}$")

# Common Egyptian mobile prefixes after +20
_MOBILE_PREFIXES = {"10", "11", "12", "15"}

# Known Egyptian carriers by prefix
_CARRIER_MAP = {
    "10": "Vodafone Egypt",
    "11": "Etisalat Egypt",
    "12": "Orange Egypt",
    "15": "WE (Telecom Egypt)",
}


def normalize_phone(raw: str) -> str:
    """Normalize an Egyptian phone number to E.164 format.

    Accepts formats like:
        01201796383        -> +201201796383
        +201201796383      -> +201201796383
        0020 1201796383    -> +201201796383
        +20-120-179-6383   -> +201201796383
        (020) 1201796383   -> +201201796383

    Raises ValueError if the number cannot be normalized to a valid
    Egyptian E.164 format.
    """
    cleaned = re.sub(r"[\s\-\(\)\.]+", "", raw.strip())

    if cleaned.startswith("0020"):
        cleaned = "+" + cleaned[2:]
    elif cleaned.startswith("020") and len(cleaned) >= 12:
        cleaned = "+" + cleaned[1:]
    elif cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    elif cleaned.startswith("0") and not cleaned.startswith("+"):
        cleaned = "+20" + cleaned[1:]
    elif not cleaned.startswith("+"):
        cleaned = "+20" + cleaned

    if not _EGYPT_E164_RE.match(cleaned):
        raise ValueError(
            f"Invalid Egyptian phone number: '{raw}' "
            f"(normalized to '{cleaned}'). "
            f"Expected format: +20XXXXXXXXX (9-10 digits after country code)."
        )
    return cleaned


def validate_phone(raw: str) -> str:
    """Validate and normalize. Alias for normalize_phone."""
    return normalize_phone(raw)


def classify_line_type(normalized: str) -> str:
    """Classify an Egyptian number as mobile, landline, or unknown.

    This is a heuristic based on prefix. For accurate classification,
    use Numverify or PhoneInfoga scanner results.
    """
    if not normalized.startswith("+20"):
        return "unknown"
    after_cc = normalized[3:]
    prefix2 = after_cc[:2]
    if prefix2 in _MOBILE_PREFIXES:
        return "mobile"
    if after_cc.startswith("2") or after_cc.startswith("3"):
        return "landline"
    return "unknown"


def guess_carrier(normalized: str) -> str:
    """Guess carrier from mobile prefix. Returns empty string if unknown."""
    if not normalized.startswith("+20"):
        return ""
    after_cc = normalized[3:]
    prefix2 = after_cc[:2]
    return _CARRIER_MAP.get(prefix2, "")


def get_phone_metadata(raw: str) -> dict:
    """Return a metadata dict for the given phone number.

    Keys: raw_input, normalized, line_type, carrier, country_code, is_voip.
    Raises ValueError on invalid input.
    """
    normalized = normalize_phone(raw)
    line_type = classify_line_type(normalized)
    return {
        "raw_input": raw,
        "normalized": normalized,
        "line_type": line_type,
        "carrier": guess_carrier(normalized),
        "country_code": "EG",
        "is_voip": line_type == "voip",
    }
