import pandas as pd

def validate_datetime_schema(df, columns, datetime_format, coerce_invalid=False):
    """
    Validate that specified columns follow a given datetime format.

    
    This function validates each non-missing value in the specified columns by
    attempting to parse it using `pd.to_datetime(..., format=datetime_format)`.
    Values that cannot be parsed under the provided format are recorded as invalid.

    By default, the function performs validation only and does not modify the input
    data. When `coerce_invalid=True`, it returns a copy of the DataFrame where
    valid values are converted to pandas datetime dtype and invalid values are set
    to `NaT`.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the datetime column(s) to validate.
    columns : list of str
        A list of datetime column names to validate. If any specified column is
        not present in `df`, a KeyError is raised.
    datetime_format : str
        Expected datetime format string used for strict validation (e.g., '%Y-%m-%d').
    coerce_invalid : bool, default False
        Whether to return a coerced copy of the DataFrame.
        - If False, only validation is performed and the data are not modified.
        - If True, valid values are converted to datetime and invalid values are
        set to `NaT` in the returned `validated_df`.

    Returns
    -------
    dict
        A validation summary containing:
        - status : {'pass', 'fail'}
            Overall validation status across all specified columns. `'pass'`
            indicates that no invalid values were detected; `'fail'` indicates
            that at least one invalid value was found.
        - validated_df : pandas.DataFrame
            A copy of the input DataFrame. If `coerce_invalid=True`, the specified
            datetime columns are converted to pandas datetime dtype (with invalid
            values set to `NaT`).
        - invalid_records : pandas.DataFrame
            A tidy DataFrame listing all invalid datetime values with columns:
            - index : index labels from `df.index` where validation failed
            - column : name of the datetime column containing the invalid value
            - raw_value : original value that failed validation

            An empty DataFrame indicates that no invalid values were detected.

    """

    # check input
    for col in columns:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in DataFrame")

    validated_df = df.copy(deep=True)
    invalid_rows = []

    for col in columns:
        for idx, value in df[col].items():

            # Skip missing values
            if pd.isna(value):
                continue

            try:
                # validate using the target format
                parsed = pd.to_datetime(value, format=datetime_format)
                if coerce_invalid:
                    validated_df.at[idx, col] = parsed

            except Exception:
                # Not matching the format will be invalid
                invalid_rows.append({"index": idx, "column": col, "raw_value": value})
                if coerce_invalid:
                    validated_df.at[idx, col] = pd.NaT

    # Force datetime dtype when coercion is enabled
    if coerce_invalid:
        for col in columns:
            validated_df[col] = pd.to_datetime(validated_df[col], errors="coerce")

    invalid_records = pd.DataFrame(invalid_rows, columns=["index", "column", "raw_value"])
    status = "pass" if invalid_records.empty else "fail"

    return {
        "status": status,
        "validated_df": validated_df,
        "invalid_records": invalid_records}
