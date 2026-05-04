"""Tests for phone number validation and normalization."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.validators import (
    classify_line_type,
    get_phone_metadata,
    guess_carrier,
    normalize_phone,
)


class TestNormalizePhone:
    """Test Egyptian phone number normalization to E.164."""

    def test_local_format(self):
        assert normalize_phone("01201796383") == "+201201796383"

    def test_e164_format(self):
        assert normalize_phone("+201201796383") == "+201201796383"

    def test_international_prefix(self):
        assert normalize_phone("00201201796383") == "+201201796383"

    def test_with_spaces(self):
        assert normalize_phone("012 0179 6383") == "+201201796383"

    def test_with_dashes(self):
        assert normalize_phone("012-0179-6383") == "+201201796383"

    def test_with_parens(self):
        assert normalize_phone("(020) 1201796383") == "+201201796383"

    def test_with_dots(self):
        assert normalize_phone("012.0179.6383") == "+201201796383"

    def test_vodafone_prefix(self):
        result = normalize_phone("01001234567")
        assert result == "+201001234567"

    def test_etisalat_prefix(self):
        result = normalize_phone("01101234567")
        assert result == "+201101234567"

    def test_orange_prefix(self):
        result = normalize_phone("01201234567")
        assert result == "+201201234567"

    def test_we_prefix(self):
        result = normalize_phone("01501234567")
        assert result == "+201501234567"

    def test_landline_cairo(self):
        result = normalize_phone("0227654321")
        assert result == "+20227654321"

    def test_invalid_too_short(self):
        with pytest.raises(ValueError, match="Invalid Egyptian phone number"):
            normalize_phone("0123456")

    def test_invalid_too_long(self):
        with pytest.raises(ValueError, match="Invalid Egyptian phone number"):
            normalize_phone("012345678901234")

    def test_invalid_non_numeric(self):
        with pytest.raises(ValueError, match="Invalid Egyptian phone number"):
            normalize_phone("abcdefghijk")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="Invalid Egyptian phone number"):
            normalize_phone("")

    def test_whitespace_stripped(self):
        assert normalize_phone("  +201201796383  ") == "+201201796383"


class TestClassifyLineType:
    def test_mobile_vodafone(self):
        assert classify_line_type("+201001234567") == "mobile"

    def test_mobile_etisalat(self):
        assert classify_line_type("+201101234567") == "mobile"

    def test_mobile_orange(self):
        assert classify_line_type("+201201234567") == "mobile"

    def test_mobile_we(self):
        assert classify_line_type("+201501234567") == "mobile"

    def test_landline_cairo(self):
        assert classify_line_type("+20227654321") == "landline"

    def test_landline_alexandria(self):
        assert classify_line_type("+20312345678") == "landline"

    def test_unknown_prefix(self):
        assert classify_line_type("+20912345678") == "unknown"

    def test_non_egyptian(self):
        assert classify_line_type("+15551234567") == "unknown"


class TestGuessCarrier:
    def test_vodafone(self):
        assert guess_carrier("+201001234567") == "Vodafone Egypt"

    def test_etisalat(self):
        assert guess_carrier("+201101234567") == "Etisalat Egypt"

    def test_orange(self):
        assert guess_carrier("+201201234567") == "Orange Egypt"

    def test_we(self):
        assert guess_carrier("+201501234567") == "WE (Telecom Egypt)"

    def test_unknown(self):
        assert guess_carrier("+20912345678") == ""


class TestGetPhoneMetadata:
    def test_returns_complete_metadata(self):
        meta = get_phone_metadata("01201796383")
        assert meta["raw_input"] == "01201796383"
        assert meta["normalized"] == "+201201796383"
        assert meta["line_type"] == "mobile"
        assert meta["carrier"] == "Orange Egypt"
        assert meta["country_code"] == "EG"
        assert meta["is_voip"] is False

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            get_phone_metadata("invalid")
