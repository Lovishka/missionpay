from sqlalchemy.orm import Session

from models import ProductData, ProductEconomics


def save_product_data(
    db: Session,
    merchant_id: int,
    df
):
    records = []

    # Keep track of economics already processed
    economics_data = {}

    for _, row in df.iterrows():

        # ----------------------------------------
        # PRODUCT DATA
        # ----------------------------------------

        record = ProductData(
            merchant_id=merchant_id,

            product_id=str(
                row.get("product_id", "")
            ),

            product_name=str(
                row.get("product_name", "")
            ),

            month=(
                str(row["month"])
                if "month" in row
                else None
            ),

            unit_sales=int(
                row.get("unit_sales", 0)
            ),

            supply_time=int(
                row.get("supply_time", 0)
            ),

            quantity_on_hand=int(
                row.get(
                    "quantity_on_hand",
                    0
                )
            )
        )

        records.append(record)

        # ----------------------------------------
        # PRODUCT ECONOMICS
        # ----------------------------------------

        selling_price = row.get(
            "selling_price"
        )

        cost_price = row.get(
            "cost_price"
        )

        max_discount = row.get(
            "max_discount_percentage"
        )

        product_id = str(
            row.get("product_id", "")
        )

        # Only create economics when pricing
        # information exists in the CSV.
        if (
            selling_price is not None
            and cost_price is not None
        ):

            economics_data[product_id] = {
                "selling_price": float(
                    selling_price
                ),
                "cost_price": float(
                    cost_price
                ),
                "max_discount_percentage": float(
                    max_discount
                    if max_discount is not None
                    else 10
                )
            }

    # ----------------------------------------
    # SAVE PRODUCT DATA
    # ----------------------------------------

    db.add_all(records)

    # ----------------------------------------
    # SAVE / UPDATE PRODUCT ECONOMICS
    # ----------------------------------------

    for product_id, values in economics_data.items():

        existing_economics = (
            db.query(ProductEconomics)
            .filter(
                ProductEconomics.merchant_id
                == merchant_id,

                ProductEconomics.product_id
                == product_id
            )
            .first()
        )

        if existing_economics:

            existing_economics.selling_price = (
                values["selling_price"]
            )

            existing_economics.cost_price = (
                values["cost_price"]
            )

            existing_economics.max_discount_percentage = (
                values[
                    "max_discount_percentage"
                ]
            )

        else:

            economics = ProductEconomics(
                merchant_id=merchant_id,

                product_id=product_id,

                selling_price=(
                    values["selling_price"]
                ),

                cost_price=(
                    values["cost_price"]
                ),

                max_discount_percentage=(
                    values[
                        "max_discount_percentage"
                    ]
                )
            )

            db.add(economics)

    # ----------------------------------------
    # COMMIT
    # ----------------------------------------

    db.commit()

    return len(records)