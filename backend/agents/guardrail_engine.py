def evaluate_offer_guardrails(
    offer_result,
    budget_limit=5000,
    max_discount_percentage=10,
    minimum_margin_percentage=10,
    approval_required=True
):
    """
    Validate an AI-generated offer before execution.

    The guardrail engine does not execute anything.
    It only determines whether the proposed action:
        - can proceed automatically
        - requires merchant approval
        - must be blocked
    """

    checks = []
    violations = []

    # --------------------------------------------------
    # 1. OFFER EXISTENCE
    # --------------------------------------------------

    if not offer_result:
        return {
            "status": "BLOCKED",
            "decision": "block",
            "reason": "No offer was generated.",
            "checks": [],
            "violations": [
                "Offer proposal is missing."
            ]
        }

    if offer_result.get("status") != "PROPOSAL_CREATED":
        return {
            "status": "BLOCKED",
            "decision": "block",
            "reason": "Offer proposal is not valid.",
            "checks": [],
            "violations": [
                offer_result.get(
                    "reason",
                    "Invalid offer proposal."
                )
            ]
        }

    offer = offer_result.get("offer", {})

    # --------------------------------------------------
    # 2. DISCOUNT LIMIT
    # --------------------------------------------------

    discount = offer.get(
        "discount_percentage",
        0
    )

    if discount <= max_discount_percentage:

        checks.append({
            "rule": "maximum_discount",
            "status": "passed",
            "value": discount,
            "limit": max_discount_percentage
        })

    else:

        checks.append({
            "rule": "maximum_discount",
            "status": "failed",
            "value": discount,
            "limit": max_discount_percentage
        })

        violations.append(
            f"Discount of {discount}% exceeds "
            f"the allowed limit of "
            f"{max_discount_percentage}%."
        )

    # --------------------------------------------------
    # 3. MARGIN PROTECTION
    # --------------------------------------------------

    selling_price = offer.get(
        "original_price"
    )

    proposed_price = offer.get(
        "proposed_price"
    )

    cost_price = offer.get(
        "cost_price"
    )

    if (
        selling_price is not None
        and proposed_price is not None
        and cost_price is not None
        and selling_price > 0
    ):

        margin_percentage = (
            (proposed_price - cost_price)
            / proposed_price
        ) * 100

        margin_percentage = round(
            margin_percentage,
            2
        )

        if margin_percentage >= minimum_margin_percentage:

            checks.append({
                "rule": "minimum_margin",
                "status": "passed",
                "value": margin_percentage,
                "limit": minimum_margin_percentage
            })

        else:

            checks.append({
                "rule": "minimum_margin",
                "status": "failed",
                "value": margin_percentage,
                "limit": minimum_margin_percentage
            })

            violations.append(
                f"Projected margin of "
                f"{margin_percentage}% is below "
                f"the minimum required margin of "
                f"{minimum_margin_percentage}%."
            )

    else:

        checks.append({
            "rule": "minimum_margin",
            "status": "failed",
            "reason": "Insufficient pricing data."
        })

        violations.append(
            "Cannot validate margin because "
            "pricing information is incomplete."
        )

    # --------------------------------------------------
    # 4. INVENTORY SAFETY
    # --------------------------------------------------

    available_stock = offer.get(
        "available_stock",
        0
    )

    if available_stock > 0:

        checks.append({
            "rule": "inventory_available",
            "status": "passed",
            "available_stock": available_stock
        })

    else:

        checks.append({
            "rule": "inventory_available",
            "status": "failed",
            "available_stock": available_stock
        })

        violations.append(
            "Product has no available inventory."
        )

    # --------------------------------------------------
    # 5. BUDGET LIMIT
    # --------------------------------------------------

        # --------------------------------------------------
    # 5. BUDGET LIMIT
    # --------------------------------------------------

    original_price = offer.get(
        "original_price"
    )

    proposed_price = offer.get(
        "proposed_price"
    )

    available_stock = offer.get(
        "available_stock",
        0
    )

    if (
        original_price is not None
        and proposed_price is not None
        and available_stock > 0
    ):

        # Cost of the discount per unit
        discount_cost_per_unit = max(
            original_price - proposed_price,
            0
        )

        # Conservative estimate:
        # evaluate the campaign against up to 100 units,
        # rather than treating the entire inventory as campaign spend.
        estimated_units = min(
            int(available_stock),
            100
        )

        estimated_budget = (
            discount_cost_per_unit
            * estimated_units
        )

        if estimated_budget <= budget_limit:

            checks.append({
                "rule": "budget_limit",
                "status": "passed",
                "estimated_exposure": round(
                    estimated_budget,
                    2
                ),
                "estimated_units": estimated_units,
                "discount_cost_per_unit": round(
                    discount_cost_per_unit,
                    2
                ),
                "limit": budget_limit
            })

        else:

            checks.append({
                "rule": "budget_limit",
                "status": "failed",
                "estimated_exposure": round(
                    estimated_budget,
                    2
                ),
                "estimated_units": estimated_units,
                "discount_cost_per_unit": round(
                    discount_cost_per_unit,
                    2
                ),
                "limit": budget_limit
            })

            violations.append(
                "Estimated promotional discount exposure "
                "exceeds the configured budget limit."
            )

    else:

        checks.append({
            "rule": "budget_limit",
            "status": "failed",
            "reason": "Insufficient pricing or inventory data."
        })

        violations.append(
            "Cannot validate promotional budget because "
            "pricing or inventory information is incomplete."
        )

    # --------------------------------------------------
    # 6. FINAL DECISION
    # --------------------------------------------------

    if violations:

        return {
            "status": "BLOCKED",
            "decision": "block",
            "reason": (
                "One or more guardrail checks failed."
            ),
            "checks": checks,
            "violations": violations
        }

    if approval_required:

        return {
            "status": "APPROVAL_REQUIRED",
            "decision": "request_approval",
            "reason": (
                "Offer passed automated guardrails "
                "but requires merchant approval."
            ),
            "checks": checks,
            "violations": []
        }

    return {
        "status": "APPROVED",
        "decision": "allow",
        "reason": (
            "Offer passed all configured guardrails."
        ),
        "checks": checks,
        "violations": []
    }