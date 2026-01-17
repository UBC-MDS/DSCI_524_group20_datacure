import pandas as pd
import pandas.testing as pdt
import pytest

from datacure.validate_categorical_schema import validate_categorical_schema  


# case 1: All values are valid (NA ignored), so status should be pass and 
# invalid_records empty
def test_validate_categorical_schema_all_valid_pass():
    df = pd.DataFrame({"color": ["red", "blue", None]}, index=[0, 2, 5])
    out = validate_categorical_schema(df, "color", ["red", "blue"])

    expected_invalid = pd.DataFrame(columns=["index", "column", "raw_value"])

    assert out["status"] == "pass"
    pdt.assert_frame_equal(out["invalid_records"], expected_invalid)


# case 2: One invalid value should be recorded with 
# correct index/column/raw_value
def test_validate_categorical_schema_single_invalid_match():
    df = pd.DataFrame({"color": ["red", "green"]}, index=[1, 3])
    out = validate_categorical_schema(df, "color", ["red", "blue"])

    expected_invalid = pd.DataFrame(
        {"index": [3], "column": ["color"], "raw_value": ["green"]}
    )

    assert out["status"] == "fail"
    pdt.assert_frame_equal(out["invalid_records"], expected_invalid)


# case 3: NA values are ignored, only non-NA invalid values are recorded
def test_validate_categorical_schema_na_ignored_only_non_na_checked():
    df = pd.DataFrame({"type": ["A", None, "C"]}, index=[10, 12, 15])
    out = validate_categorical_schema(df, "type", ["A", "B"])

    expected_invalid = pd.DataFrame(
        {"index": [15], "column": ["type"], "raw_value": ["C"]}
    )

    assert out["status"] == "fail"
    pdt.assert_frame_equal(out["invalid_records"], expected_invalid)


# case 4: Missing column should raise KeyError
def test_validate_categorical_schema_missing_column_raises_keyerror():
    df = pd.DataFrame({"other": ["red"]}, index=[0])
    with pytest.raises(KeyError):
        validate_categorical_schema(df, "color", ["red", "blue"])


# case 5: Empty df should raise ValueError
def test_validate_categorical_schema_empty_df_raises_valueerror():
    df = pd.DataFrame()
    with pytest.raises(ValueError):
        validate_categorical_schema(df, "color", ["red", "blue"])


# case 6: Empty allowed_categories should raise ValueError
def test_empty_allowed_categories():
    df = pd.DataFrame({"color": ["red"]}, index=[0])
    with pytest.raises(ValueError):
        validate_categorical_schema(df, "color", [])
