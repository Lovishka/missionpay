def calculate_product_opportunity(product):
    """
    Rank a product for promotional consideration.

    This is a deterministic prototype rule engine.
    It does NOT claim causal relationships between weather
    and product demand.
    """

    stock_risk = product.get("stock_risk")
    stock_days = product.get("estimated_stock_days", 0)
    trend = product.get("trend_percentage", 0)
    demand_level = product.get("demand_level")

    score = 0
    reasons = []
    warnings = []

    # ----------------------------------------
    # INVENTORY SAFETY
    # ----------------------------------------

    if stock_risk == "critical":
        return {
            "score": 0,
            "priority": "do_not_promote",
            "reasons": [
                "Current inventory is critically low."
            ],
            "warnings": [
                "Promotional activity could increase stockout risk."
            ]
        }

    if stock_risk == "high":
        score += 10
        warnings.append(
            "Inventory is relatively constrained."
        )

    elif stock_risk == "medium":
        score += 25
        reasons.append(
            "Inventory is available but should be monitored."
        )

    elif stock_risk == "low":
        score += 40
        reasons.append(
            "Inventory risk is currently low."
        )

    # ----------------------------------------
    # STOCK COVERAGE
    # ----------------------------------------

    if stock_days >= 10:
        score += 30
        reasons.append(
            f"Approximately {stock_days:.1f} days of stock available."
        )

    elif stock_days >= 6:
        score += 20
        reasons.append(
            f"Approximately {stock_days:.1f} days of stock available."
        )

    elif stock_days >= 3:
        score += 10

    else:
        warnings.append(
            "Limited stock coverage."
        )

    # ----------------------------------------
    # DEMAND / TREND
    # ----------------------------------------

    if trend > 5:
        score += 20
        reasons.append(
            "Recent sales trend is positive."
        )

    elif trend >= 0:
        score += 10
        reasons.append(
            "Recent sales trend is stable or slightly positive."
        )

    else:
        warnings.append(
            "Recent sales trend is declining."
        )

    # ----------------------------------------
    # DEMAND LEVEL
    # ----------------------------------------

    if demand_level == "high":
        score += 15
        reasons.append(
            "Model indicates high demand."
        )

    elif demand_level == "medium":
        score += 10

    # ----------------------------------------
    # FINAL PRIORITY
    # ----------------------------------------

    if score >= 70:
        priority = "high"

    elif score >= 45:
        priority = "medium"

    else:
        priority = "low"

    return {
        "score": score,
        "priority": priority,
        "reasons": reasons,
        "warnings": warnings
    }


def generate_opportunities(weather, events, products):
    """
    Convert local signals and ML demand information
    into actionable product opportunities.
    """

    opportunities = []

    # ----------------------------------------
    # WEATHER SIGNAL
    # ----------------------------------------

    apparent_temperature = weather.get("apparent_temperature")

    weather_signal = None

    if apparent_temperature is not None:

        if apparent_temperature >= 35:
            weather_signal = {
                "signal": "high_heat",
                "severity": "high",
                "value": apparent_temperature,
                "unit": "°C"
            }

        elif apparent_temperature >= 30:
            weather_signal = {
                "signal": "warm_weather",
                "severity": "medium",
                "value": apparent_temperature,
                "unit": "°C"
            }

    # ----------------------------------------
    # EVENT SIGNAL
    # ----------------------------------------

    event_signal = None

    if events:
        event_signal = {
            "signal": "nearby_events",
            "event_count": len(events)
        }

    # ----------------------------------------
    # RANK PRODUCTS
    # ----------------------------------------

    ranked_products = []

    for product in products:

        analysis = calculate_product_opportunity(product)

        ranked_products.append({
            "product_id": product.get("product_id"),
            "product_name": product.get("product_name"),
            "score": analysis["score"],
            "priority": analysis["priority"],
            "current_stock": product.get("current_stock"),
            "stock_days": product.get("estimated_stock_days"),
            "stock_risk": product.get("stock_risk"),
            "predicted_demand": product.get(
                "predicted_next_month_demand"
            ),
            "trend_percentage": product.get(
                "trend_percentage"
            ),
            "reasons": analysis["reasons"],
            "warnings": analysis["warnings"]
        })

    ranked_products.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # ----------------------------------------
    # SAFE PROMOTION CANDIDATES
    # ----------------------------------------

    candidates = [
        product
        for product in ranked_products
        if product["priority"] in ["high", "medium"]
        and product["stock_risk"] != "critical"
    ]

    # ----------------------------------------
    # OVERALL STATUS
    # ----------------------------------------

    if candidates and (weather_signal or event_signal):

        status = "OPPORTUNITY_DETECTED"

        next_action = (
            "Offer Agent should evaluate the highest-ranked "
            "products against the merchant's mission goal "
            "and business constraints."
        )

    elif candidates:

        status = "PRODUCT_OPPORTUNITY"

        next_action = (
            "Products with sufficient inventory are available "
            "for further offer evaluation."
        )

    else:

        status = "CONSTRAINT_DETECTED"

        next_action = (
            "No product currently meets the inventory criteria "
            "for promotional consideration."
        )

    return {
        "status": status,

        "signals": {
            "weather": weather_signal,
            "events": event_signal
        },

        "ranked_products": ranked_products,

        "promotion_candidates": candidates,

        "next_action": next_action
    }