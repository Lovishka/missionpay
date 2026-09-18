def analyze_weather(weather: dict, products: list):
    temperature = weather.get("temperature")
    apparent_temperature = weather.get("apparent_temperature")
    rain = weather.get("rain", 0)

    signals = []
    relevant_products = []

    # Weather signals only describe the environment.
    if apparent_temperature is not None:
        if apparent_temperature >= 35:
            signals.append({
                "type": "heat",
                "severity": "high",
                "message": "High apparent temperature detected."
            })
        elif apparent_temperature >= 30:
            signals.append({
                "type": "heat",
                "severity": "medium",
                "message": "Warm conditions detected."
            })

    if rain is not None and rain > 2:
        signals.append({
            "type": "rain",
            "severity": "medium",
            "message": "Rain detected."
        })

    # Connect weather to ACTUAL merchant products.
    for product in products:
        predicted_demand = product.get("predicted_next_month_demand", 0)
        current_stock = product.get("current_stock", 0)

        if predicted_demand <= 0:
            continue

        # We do NOT assume what the product is.
        # We simply surface products for which
        # demand and inventory information exists.
        relevant_products.append({
            "product_id": product.get("product_id"),
            "product_name": product.get("product_name"),
            "predicted_demand": predicted_demand,
            "current_stock": current_stock,
            "stock_risk": product.get("stock_risk"),
            "demand_level": product.get("demand_level")
        })

    # No product-specific recommendation is made
    # until the actual merchant data supports it.
    if signals and relevant_products:
        opportunity = (
            "Weather conditions may affect local demand. "
            "Merchant product and demand data are available "
            "for further opportunity analysis."
        )
    elif signals:
        opportunity = (
            "Weather signal detected, but insufficient "
            "merchant product evidence for a product-specific opportunity."
        )
    else:
        opportunity = (
            "No significant weather signal detected."
        )

    return {
        "weather_signals": signals,
        "relevant_products": relevant_products,
        "opportunity": opportunity
    }