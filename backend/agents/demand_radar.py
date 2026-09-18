from typing import Dict, List

from sqlalchemy.orm import Session

from models import ProductData
from ml.demand_model import DemandForecastModel


class DemandRadarAgent:

    def __init__(self):
        self.forecast_model = DemandForecastModel()

    def analyze(
        self,
        db: Session,
        merchant_id: int
    ) -> Dict:

        rows = (
            db.query(ProductData)
            .filter(
                ProductData.merchant_id == merchant_id
            )
            .order_by(
                ProductData.product_id,
                ProductData.month
            )
            .all()
        )

        if not rows:
            return {
                "status": "no_data",
                "message": "No merchant data available.",
                "products": [],
                "insights": []
            }

        # Group historical data by product
        grouped = {}

        for row in rows:

            product_id = str(row.product_id)

            if product_id not in grouped:
                grouped[product_id] = []

            grouped[product_id].append({
                "month": int(row.month),
                "sales": float(row.unit_sales),
                "stock": float(row.quantity_on_hand),
                "supply_time": float(row.supply_time)
            })

        # Load trained model
        try:
            self.forecast_model.load()
        except FileNotFoundError:

            return {
                "status": "model_not_trained",
                "message": (
                    "Demand model has not been trained yet."
                ),
                "products": [],
                "insights": []
            }

        analyzed_products: List[Dict] = []

        for product_id, history in grouped.items():

            history.sort(
                key=lambda x: x["month"]
            )

            product_name = (
                db.query(ProductData.product_name)
                .filter(
                    ProductData.merchant_id == merchant_id,
                    ProductData.product_id == product_id
                )
                .first()
            )

            if not product_name:
                continue

            product_name = product_name[0]

            latest = history[-1]

            current_stock = latest["stock"]
            supply_time = latest["supply_time"]

            total_sales = sum(
                item["sales"]
                for item in history
            )

            average_sales = (
                total_sales / len(history)
            )

            # ML forecast
            predicted_demand = (
                self.forecast_model.predict_next_month(
                    history,
                    supply_time
                )
            )

            # Historical trend
            recent_sales = [
                item["sales"]
                for item in history[-3:]
            ]

            recent_average = (
                sum(recent_sales)
                / len(recent_sales)
            )

            if average_sales > 0:

                trend_percentage = (
                    (recent_average - average_sales)
                    / average_sales
                ) * 100

            else:
                trend_percentage = 0

            # Stock coverage based on predicted demand
            predicted_daily_demand = (
                predicted_demand / 30
            )

            if predicted_daily_demand > 0:

                stock_days = (
                    current_stock
                    / predicted_daily_demand
                )

            else:

                stock_days = 999

            # Inventory requirement
            safety_days = 7

            required_stock = (
                predicted_daily_demand
                * (supply_time + safety_days)
            )

            reorder_quantity = max(
                int(required_stock - current_stock),
                0
            )

            # Demand level
            if predicted_demand >= 10000:
                demand_level = "very_high"

            elif predicted_demand >= 7000:
                demand_level = "high"

            elif predicted_demand >= 4000:
                demand_level = "medium"

            else:
                demand_level = "low"

            # Stock risk
            if stock_days <= supply_time:

                stock_risk = "critical"

            elif stock_days <= supply_time + 3:

                stock_risk = "high"

            elif stock_days <= supply_time + 7:

                stock_risk = "medium"

            else:

                stock_risk = "low"

            # Recommendation
            if stock_risk == "critical":

                recommendation = (
                    "Urgent replenishment recommended "
                    "before expected demand arrives."
                )

            elif stock_risk == "high":

                recommendation = (
                    "Replenish inventory soon to avoid "
                    "potential stockout."
                )

            elif trend_percentage > 15:

                recommendation = (
                    "Demand is trending upward. "
                    "Consider increasing inventory."
                )

            elif demand_level in ["very_high", "high"]:

                recommendation = (
                    "Strong predicted demand. "
                    "Consider promotion and sufficient stock."
                )

            else:

                recommendation = (
                    "Maintain current inventory strategy."
                )

            analyzed_products.append({

                "product_id": product_id,

                "product_name": product_name,

                "historical_units_sold": round(
                    total_sales,
                    2
                ),

                "average_monthly_sales": round(
                    average_sales,
                    2
                ),

                "recent_3_month_average": round(
                    recent_average,
                    2
                ),

                "trend_percentage": round(
                    trend_percentage,
                    2
                ),

                "predicted_next_month_demand": round(
                    predicted_demand,
                    2
                ),

                "current_stock": round(
                    current_stock,
                    2
                ),

                "supply_time_days": round(
                    supply_time,
                    2
                ),

                "estimated_stock_days": round(
                    stock_days,
                    2
                ),

                "demand_level": demand_level,

                "stock_risk": stock_risk,

                "recommended_reorder_quantity":
                    reorder_quantity,

                "recommendation":
                    recommendation
            })

        # Sort by predicted demand
        analyzed_products.sort(
            key=lambda x:
                x["predicted_next_month_demand"],
            reverse=True
        )

        insights = []

        if analyzed_products:

            top_product = analyzed_products[0]

            insights.append({

                "type": "demand_opportunity",

                "priority": "high",

                "product_id":
                    top_product["product_id"],

                "message": (
                    f"{top_product['product_name']} has "
                    f"the highest predicted demand at "
                    f"{top_product['predicted_next_month_demand']:.0f} "
                    f"units next month."
                )
            })

        for product in analyzed_products:

            if product["stock_risk"] in [
                "critical",
                "high"
            ]:

                insights.append({

                    "type": "inventory_risk",

                    "priority":
                        product["stock_risk"],

                    "product_id":
                        product["product_id"],

                    "message": (
                        f"{product['product_name']} has "
                        f"{product['stock_risk']} stock risk. "
                        f"Recommended reorder: "
                        f"{product['recommended_reorder_quantity']} "
                        f"units."
                    )
                })

        return {

            "status": "success",

            "agent": "Demand Radar Agent",

            "merchant_id": merchant_id,

            "model": "Random Forest Regressor",

            "products_analyzed":
                len(analyzed_products),

            "products":
                analyzed_products,

            "insights":
                insights
        }