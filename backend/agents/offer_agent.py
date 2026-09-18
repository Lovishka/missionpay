def generate_offer(
    mission_goal,
    product,
    weather_signal=None,
    event_signal=None
):
    """
    Generate an offer proposal from an approved product candidate.

    This agent proposes an action.
    It does not execute the action.
    """

    if not product:
        return {
            "status": "NO_PRODUCT",
            "message": "No eligible product found."
        }

    product_name = product.get("product_name")
    current_stock = product.get("current_stock", 0)
    stock_risk = product.get("stock_risk")

    selling_price = product.get("selling_price")
    cost_price = product.get("cost_price")

    max_discount = product.get(
        "max_discount_percentage",
        10
    )

    # ----------------------------------------
    # INVENTORY SAFETY
    # ----------------------------------------

    if stock_risk == "critical":
        return {
            "status": "REJECTED",
            "reason": (
                f"{product_name} has critical inventory "
                "and should not be promoted."
            )
        }

    # ----------------------------------------
    # PRICE VALIDATION
    # ----------------------------------------

    if selling_price is None or cost_price is None:
        return {
            "status": "INSUFFICIENT_DATA",
            "reason": (
                "Selling price and cost price are required "
                "before generating a financially valid offer."
            )
        }

    selling_price = float(selling_price)
    cost_price = float(cost_price)
    max_discount = float(max_discount)

    if selling_price <= cost_price:
        return {
            "status": "REJECTED",
            "reason": (
                "Selling price is not greater than cost price."
            )
        }

    # ----------------------------------------
    # DISCOUNT CALCULATION
    # ----------------------------------------

    proposed_discount = min(
        max_discount,
        10
    )

    discounted_price = round(
        selling_price * (
            1 - proposed_discount / 100
        ),
        2
    )

    # ----------------------------------------
    # COST PROTECTION
    # ----------------------------------------

    if discounted_price < cost_price:

        proposed_discount = round(
            (
                (selling_price - cost_price)
                / selling_price
            ) * 100,
            2
        )

        discounted_price = round(
            selling_price * (
                1 - proposed_discount / 100
            ),
            2
        )

    # ----------------------------------------
    # MARGIN CALCULATION
    # ----------------------------------------

    margin_before = round(
        (
            (selling_price - cost_price)
            / selling_price
        ) * 100,
        2
    )

    margin_after = round(
        (
            (discounted_price - cost_price)
            / discounted_price
        ) * 100,
        2
    )

    # ----------------------------------------
    # REASONING
    # ----------------------------------------

    reasons = []

    if product.get("stock_risk") == "low":
        reasons.append(
            "Inventory risk is low."
        )

    if product.get("stock_days", 0) >= 6:
        reasons.append(
            f"{product.get('stock_days'):.1f} days "
            "of inventory coverage is available."
        )

    if product.get("trend_percentage", 0) >= 0:
        reasons.append(
            "Recent sales trend is stable or positive."
        )
    else:
        reasons.append(
            "Recent sales trend is declining."
        )

    if weather_signal:
        reasons.append(
            "A current weather signal is available "
            "as additional local context."
        )

    if event_signal:
        reasons.append(
            "A verified nearby event is available "
            "as additional local context."
        )

    # ----------------------------------------
    # OFFER
    # ----------------------------------------

    offer = {
        "product_id": product.get("product_id"),
        "product_name": product_name,

        "offer_type": "percentage_discount",

        "original_price": selling_price,

        "discount_percentage": proposed_discount,

        "proposed_price": discounted_price,

        "cost_price": cost_price,

        "margin_before": margin_before,

        "margin_after": margin_after,

        "available_stock": current_stock
    }

    return {
        "status": "PROPOSAL_CREATED",

        "mission_goal": mission_goal,

        "offer": offer,

        "reasoning": reasons,

        "requires_approval": True,

        "execution_status": "NOT_EXECUTED"
    }