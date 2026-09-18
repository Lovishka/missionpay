import pandas as pd


# Supported variations for each business field
COLUMN_ALIASES = {
    "product_id": [
        "product_id",
        "productid",
        "product id",
        "id",
        "sku",
        "item_id",
    ],
    "product_name": [
        "product_name",
        "productname",
        "product name",
        "product",
        "item",
        "item_name",
    ],
    "month": [
        "month",
        "date",
        "sale_date",
        "sales_date",
    ],
    "unit_sales": [
        "unit_sales",
        "units_sold",
        "unit_sold",
        "quantity_sold",
        "sales",
        "units",
    ],
    "supply_time": [
        "supply_time",
        "supply time",
        "lead_time",
        "lead time",
        "supplier_lead_time",
    ],
    "quantity_on_hand": [
        "quantity_on_hand",
        "quantity on hand",
        "stock",
        "inventory",
        "stock_quantity",
        "current_stock",
    ],
    "selling_price": [
    "selling_price",
    "price",
    "sellingprice"
],

"cost_price": [
    "cost_price",
    "cost",
    "costprice"
],

"max_discount_percentage": [
    "max_discount_percentage",
    "max_discount",
    "discount_limit"
],
}


def normalize_column_name(column: str) -> str:
    """
    Convert column names into a consistent format.
    """

    return (
        str(column)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def detect_columns(df: pd.DataFrame) -> dict:
    """
    Detect business fields from uploaded CSV columns.
    """

    detected = {}

    normalized_columns = {
        normalize_column_name(column): column
        for column in df.columns
    }

    for field, aliases in COLUMN_ALIASES.items():

        for alias in aliases:

            normalized_alias = normalize_column_name(alias)

            if normalized_alias in normalized_columns:

                detected[field] = normalized_columns[
                    normalized_alias
                ]

                break

    return detected


def validate_data(df: pd.DataFrame, detected: dict) -> dict:

    errors = []
    warnings = []

    # Required fields
    required_fields = [
        "product_id",
        "product_name",
        "unit_sales",
        "quantity_on_hand",
    ]

    for field in required_fields:

        if field not in detected:

            errors.append(
                f"Required column not found: {field}"
            )

    if errors:

        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
        }

    # Check empty dataframe
    if df.empty:

        errors.append(
            "CSV contains no data rows."
        )

        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
        }

    # Check missing values
    for field, column in detected.items():

        missing = int(
            df[column].isna().sum()
        )

        if missing > 0:

            warnings.append(
                f"{column}: {missing} missing values"
            )

    # Check numeric fields
    for field in [
        "unit_sales",
        "quantity_on_hand",
        "supply_time",
    ]:

        if field in detected:

            column = detected[field]

            numeric_values = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            invalid_count = int(
                numeric_values.isna().sum()
            )

            if invalid_count > 0:

                warnings.append(
                    f"{column}: "
                    f"{invalid_count} non-numeric values"
                )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def clean_data(
    df: pd.DataFrame,
    detected: dict
) -> pd.DataFrame:

    rename_mapping = {
        column: field
        for field, column in detected.items()
    }

    clean_df = df.rename(
        columns=rename_mapping
    ).copy()

    # Numeric conversion
    for field in [
        "unit_sales",
        "quantity_on_hand",
        "supply_time",
    ]:

        if field in clean_df.columns:

            clean_df[field] = pd.to_numeric(
                clean_df[field],
                errors="coerce"
            )

    # Remove rows without product ID
    if "product_id" in clean_df.columns:

        clean_df = clean_df.dropna(
            subset=["product_id"]
        )

    # Normalize product names
    if "product_name" in clean_df.columns:

        clean_df["product_name"] = (
            clean_df["product_name"]
            .astype(str)
            .str.strip()
        )

    # Fill numeric missing values
    for field in [
        "unit_sales",
        "quantity_on_hand",
        "supply_time",
    ]:

        if field in clean_df.columns:

            clean_df[field] = (
                clean_df[field]
                .fillna(0)
            )

    return clean_df


def process_csv(file_path: str) -> dict:

    try:

        df = pd.read_csv(file_path)

    except Exception as e:

        return {
            "success": False,
            "errors": [
                f"Unable to read CSV: {str(e)}"
            ],
        }

    detected = detect_columns(df)

    validation = validate_data(
        df,
        detected
    )

    if not validation["valid"]:

        return {
            "success": False,
            "errors": validation["errors"],
            "warnings": validation["warnings"],
            "detected_columns": detected,
        }

    clean_df = clean_data(
        df,
        detected
    )

    return {
        "success": True,
        "data": clean_df,
        "detected_columns": detected,
        "warnings": validation["warnings"],
        "row_count": len(clean_df),
        "column_count": len(clean_df.columns),
    }