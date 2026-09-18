import os
import joblib
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


MODEL_DIR = "ml/saved_models"
MODEL_PATH = os.path.join(
    MODEL_DIR,
    "demand_forecast_model.joblib"
)


class DemandForecastModel:

    def __init__(self):
        self.model = None
        self.products = []
        self.metrics = {}

    def prepare_features(self, rows):
        """
        Convert historical product data into supervised
        machine-learning features.
        """

        data = []

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

        for product_id, history in grouped.items():

            history.sort(key=lambda x: x["month"])

            for i in range(3, len(history)):

                current = history[i]

                lag_1 = history[i - 1]["sales"]
                lag_2 = history[i - 2]["sales"]
                lag_3 = history[i - 3]["sales"]

                rolling_3 = np.mean([
                    lag_1,
                    lag_2,
                    lag_3
                ])

                month = current["month"]

                features = [
                    month,
                    np.sin(2 * np.pi * month / 12),
                    np.cos(2 * np.pi * month / 12),
                    lag_1,
                    lag_2,
                    lag_3,
                    rolling_3,
                    history[i - 1]["stock"],
                    current["supply_time"]
                ]

                target = current["sales"]

                data.append({
                    "product_id": product_id,
                    "features": features,
                    "target": target
                })

        return data

    def train(self, rows):

        training_data = self.prepare_features(rows)

        if len(training_data) < 20:
            raise ValueError(
                "Not enough historical data to train demand model."
            )

        # Time-aware split:
        # last observation of each product is reserved for validation.
        train_data = []
        test_data = []

        grouped = {}

        for item in training_data:

            product_id = item["product_id"]

            if product_id not in grouped:
                grouped[product_id] = []

            grouped[product_id].append(item)

        for product_id, history in grouped.items():

            if len(history) >= 2:
                train_data.extend(history[:-1])
                test_data.append(history[-1])
            else:
                train_data.extend(history)

        X_train = np.array([
            item["features"]
            for item in train_data
        ])

        y_train = np.array([
            item["target"]
            for item in train_data
        ])

        X_test = np.array([
            item["features"]
            for item in test_data
        ])

        y_test = np.array([
            item["target"]
            for item in test_data
        ])

        self.model = RandomForestRegressor(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=2,
            random_state=42
        )

        self.model.fit(
            X_train,
            y_train
        )

        predictions = self.model.predict(X_test)

        mae = mean_absolute_error(
            y_test,
            predictions
        )

        rmse = np.sqrt(
            mean_squared_error(
                y_test,
                predictions
            )
        )

        self.metrics = {
            "mae": round(float(mae), 2),
            "rmse": round(float(rmse), 2),
            "training_samples": len(X_train),
            "validation_samples": len(X_test)
        }

        os.makedirs(
            MODEL_DIR,
            exist_ok=True
        )

        joblib.dump(
            self.model,
            MODEL_PATH
        )

        return self.metrics

    def load(self):

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Demand model has not been trained yet."
            )

        self.model = joblib.load(
            MODEL_PATH
        )

        return True

    def predict_next_month(
        self,
        history,
        supply_time
    ):

        if self.model is None:
            self.load()

        history = sorted(
            history,
            key=lambda x: x["month"]
        )

        if len(history) < 3:
            raise ValueError(
                "At least 3 months of history are required."
            )

        lag_1 = float(history[-1]["sales"])
        lag_2 = float(history[-2]["sales"])
        lag_3 = float(history[-3]["sales"])

        rolling_3 = np.mean([
            lag_1,
            lag_2,
            lag_3
        ])

        current_month = int(
            history[-1]["month"]
        )

        next_month = (
            current_month % 12
        ) + 1

        features = np.array([[
            next_month,
            np.sin(
                2 * np.pi * next_month / 12
            ),
            np.cos(
                2 * np.pi * next_month / 12
            ),
            lag_1,
            lag_2,
            lag_3,
            rolling_3,
            float(history[-1]["stock"]),
            float(supply_time)
        ]])

        prediction = self.model.predict(
            features
        )[0]

        return max(
            0,
            round(float(prediction), 2)
        )