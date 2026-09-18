import re
from typing import Dict


class GoalPlannerAgent:
    """
    Goal Planner Agent

    Converts a merchant's natural-language goal into
    a structured mission.
    """

    def analyze_goal(self, goal: str) -> Dict:
        goal = goal.strip()

        if not goal:
            raise ValueError("Goal cannot be empty")

        goal_lower = goal.lower()

        # -----------------------------------------
        # 1. Detect goal type
        # -----------------------------------------

        if any(word in goal_lower for word in [
            "sales",
            "sale",
            "revenue",
            "kamai",
            "bikri"
        ]):
            goal_type = "sales_growth"

        elif any(word in goal_lower for word in [
            "customer",
            "customers",
            "customer laane",
            "customers laane"
        ]):
            goal_type = "customer_acquisition"

        elif any(word in goal_lower for word in [
            "inventory",
            "stock",
            "stok"
        ]):
            goal_type = "inventory"

        else:
            goal_type = "general_business"

        # -----------------------------------------
        # 2. Extract monetary target
        # -----------------------------------------

        target = self._extract_amount(goal)

        # -----------------------------------------
        # 3. Detect deadline
        # -----------------------------------------

        deadline = self._extract_deadline(goal_lower)

        # -----------------------------------------
        # 4. Determine priority
        # -----------------------------------------

        if goal_type == "sales_growth":
            priority = "revenue"

        elif goal_type == "customer_acquisition":
            priority = "customers"

        elif goal_type == "inventory":
            priority = "inventory"

        else:
            priority = "business_growth"

        # -----------------------------------------
        # 5. Create action plan
        # -----------------------------------------

        action_plan = self._generate_action_plan(goal_type)

        return {
            "original_goal": goal,
            "goal_type": goal_type,
            "target": target,
            "deadline": deadline,
            "priority": priority,
            "action_plan": action_plan
        }

    # =========================================
    # Extract monetary amount
    # =========================================
    def _extract_amount(self, goal: str):
        """
    Extract monetary target from natural-language goals.

    Supports:
    ₹20,000
    ₹20000
    Rs 20000
    Rs. 20,000
    20000 rupees
    20k
    20K
    get 50000 sales
    achieve 50000 revenue
    sales of 50000
    """

        patterns = [
        # ₹20,000 / ₹20000 / ₹20.5k
        r"₹\s*([\d,]+(?:\.\d+)?)\s*k?",
        
        # Rs 20,000 / Rs. 20,000 / Rs 20k
        r"rs\.?\s*([\d,]+(?:\.\d+)?)\s*k?",
        
        # 20,000 rupees / 20000 rupees
        r"([\d,]+(?:\.\d+)?)\s*k?\s*rupees?",
        
        # Plain number followed by sales/revenue
        # Example: 50000 sales
        r"([\d,]+(?:\.\d+)?)\s*(?:sales?|revenue)",
        
        # sales/revenue followed by amount
        # Example: sales of 50000
        r"(?:sales?|revenue)\s*(?:of|target)?\s*₹?\s*([\d,]+(?:\.\d+)?)\s*k?",
        
        # Generic 20k
        r"([\d,]+(?:\.\d+)?)\s*k\b"]

        for pattern in patterns:

            match = re.search(
            pattern,
            goal,
            re.IGNORECASE
        )

            if match:
                value = match.group(1).replace(",", "")

                try:
                    number = float(value)

                # Convert k → thousand
                    if re.search(r"\bk\b", match.group(0), re.IGNORECASE):
                        number *= 1000

                    return int(number)

                except ValueError:
                     pass

        return None
    # =========================================
    # Extract deadline
    # =========================================

    def _extract_deadline(self, goal_lower: str):

        if any(word in goal_lower for word in [
            "today",
            "aaj"
        ]):
            return "today"

        if any(word in goal_lower for word in [
            "tomorrow",
            "kal"
        ]):
            return "tomorrow"

        if any(word in goal_lower for word in [
            "this week",
            "iss week",
            "is week"
        ]):
            return "this_week"

        if any(word in goal_lower for word in [
            "this month",
            "iss month",
            "is month"
        ]):
            return "this_month"

        return "unspecified"

    # =========================================
    # Generate action plan
    # =========================================

    def _generate_action_plan(self, goal_type: str):

        if goal_type == "sales_growth":

            return [
                "Analyze current sales",
                "Detect local demand",
                "Identify target customers",
                "Recommend inventory",
                "Create personalized offer",
                "Prepare campaign",
                "Monitor revenue",
                "Adapt actions based on results"
            ]

        if goal_type == "customer_acquisition":

            return [
                "Analyze existing customers",
                "Identify potential customers",
                "Create acquisition offer",
                "Prepare campaign",
                "Monitor customer response",
                "Adapt campaign"
            ]

        if goal_type == "inventory":

            return [
                "Analyze current inventory",
                "Detect demand trends",
                "Identify stock gaps",
                "Recommend replenishment",
                "Monitor inventory levels"
            ]

        return [
            "Analyze business context",
            "Identify opportunities",
            "Generate action plan",
            "Execute approved actions",
            "Measure results",
            "Adapt strategy"
        ]