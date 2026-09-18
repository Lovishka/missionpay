import os
import io
import requests
import re
import pandas as pd 
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Base, engine, get_db
from models import Merchant, User, ProductData, ProductEconomics
from services.weather_service import get_current_weather
from agents.goal_planner import GoalPlannerAgent
from auth.routes import router as auth_router
from auth.dependencies import get_current_user

from data.csv_processor import process_csv
from services.csv_service import save_product_data

from agents.demand_radar import DemandRadarAgent
from ml.demand_model import DemandForecastModel

from agents.offer_agent import generate_offer
from agents.guardrail_engine import evaluate_offer_guardrails
from agents.opportunity_engine import generate_opportunities
from services.event_service import get_nearby_events
from agents.weather_analyzer import analyze_weather
# --------------------------------------------------
# APP
# --------------------------------------------------

app = FastAPI(
    title="MissionPay API",
    description="AI-powered Local Commerce Autopilot",
    version="1.0.0"
)

def extract_target_from_goal(goal: str):
    match = re.search(
        r'(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)',
        goal,
        re.IGNORECASE
    )

    if not match:
        return None

    return float(match.group(1).replace(",", ""))
# Create database tables
Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# ROUTERS
# --------------------------------------------------

app.include_router(auth_router)


# --------------------------------------------------
# MISSION MODELS
# --------------------------------------------------

class MissionRequest(BaseModel):
    goal: str


class MissionResponse(BaseModel):
    goal: str
    goal_type: str
    target: int | None
    deadline: str
    priority: str
    current_revenue: int | None
    revenue_gap: int | None
    status: str
    action_plan: list[str]


goal_planner = GoalPlannerAgent()
demand_radar = DemandRadarAgent()
demand_model = DemandForecastModel()

class MerchantLocationRequest(BaseModel):
    city: str
    latitude: float
    longitude: float
# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "MissionPay API is running 🚀"
    }
@app.get("/api/radar/local-commerce")
def local_commerce_radar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Get merchant
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == current_user.merchant_id)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant not found"
        )

    if not merchant.latitude or not merchant.longitude:
        raise HTTPException(
            status_code=400,
            detail="Merchant location is not configured"
        )

    latitude = float(merchant.latitude)
    longitude = float(merchant.longitude)

    # 2. Get real weather
    weather = get_current_weather(
        latitude,
        longitude
    )

    # 3. Get nearby verified events
    try:
        events = get_nearby_events(
            latitude=latitude,
            longitude=longitude,
            radius_km=10,
            limit=10
        )
    except requests.RequestException:
        events = []

    # 4. Get existing Demand Radar
    demand_result = demand_radar.analyze(
        db=db,
        merchant_id=current_user.merchant_id
    )

    products = demand_result.get("products", [])

    # 5. Analyze weather against actual merchant data
    weather_analysis = analyze_weather(
        weather=weather,
        products=products
    )
    opportunity_result = generate_opportunities(
    weather=weather,
    events=events,
    products=products
    )

    # 6. Build commerce opportunities
    opportunities = []

    if weather_analysis["weather_signals"]:
        opportunities.append({
            "type": "weather",
            "signal": weather_analysis["weather_signals"],
            "reason": (
                "Weather conditions may influence "
                "local customer demand."
            )
        })

    if events:
        opportunities.append({
            "type": "event",
            "events": events,
            "reason": (
                "Verified upcoming events were found "
                "near the merchant."
            )
        })

    # 7. Inventory opportunities
    critical_products = [
        product
        for product in products
        if product.get("stock_risk") == "critical"
    ]

    if critical_products:
        opportunities.append({
            "type": "inventory",
            "products": [
                {
                    "product_id": p.get("product_id"),
                    "product_name": p.get("product_name"),
                    "predicted_demand": p.get(
                        "predicted_next_month_demand"
                    ),
                    "current_stock": p.get(
                        "current_stock"
                    ),
                    "stock_risk": p.get(
                        "stock_risk"
                    )
                }
                for p in critical_products
            ],
            "reason": (
                "Products with critical inventory "
                "risk were detected."
            )
        })

    return {
        "status": "success",

        "merchant": {
            "business_name": merchant.business_name,
            "city": merchant.city,
            "latitude": latitude,
            "longitude": longitude
        },

        "context": {
            "weather": weather,
            "events": events
        },

        "demand": {
            "model": demand_result.get("model"),
            "products_analyzed": demand_result.get(
                "products_analyzed"
            ),
            "products": products
        },

        "opportunity_engine": opportunity_result
    }
@app.get("/api/radar/weather-analysis")
def weather_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == current_user.merchant_id)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant not found"
        )

    if not merchant.latitude or not merchant.longitude:
        raise HTTPException(
            status_code=400,
            detail="Merchant location is not configured"
        )

    # 1. Get real weather
    weather = get_current_weather(
        float(merchant.latitude),
        float(merchant.longitude)
    )

    # 2. Get existing Demand Radar analysis
    demand_result = demand_radar.analyze(
        db=db,
        merchant_id=current_user.merchant_id
    )

    # 3. Extract products analyzed by Demand Radar
    products = demand_result.get("products", [])

    # 4. Combine weather + actual merchant data
    analysis = analyze_weather(
        weather=weather,
        products=products
    )

    return {
        "status": "success",

        "merchant": {
            "business_name": merchant.business_name,
            "city": merchant.city,
            "latitude": float(merchant.latitude),
            "longitude": float(merchant.longitude)
        },

        "weather": weather,

        "demand_radar": {
            "model": demand_result.get("model"),
            "products_analyzed": demand_result.get("products_analyzed"),
            "products": products
        },

        "commerce_analysis": analysis
    }
@app.get("/api/radar/events")
def nearby_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == current_user.merchant_id)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant not found"
        )

    if not merchant.latitude or not merchant.longitude:
        raise HTTPException(
            status_code=400,
            detail="Merchant location is not configured"
        )

    try:
        events = get_nearby_events(
            latitude=float(merchant.latitude),
            longitude=float(merchant.longitude),
            radius_km=10,
            limit=10
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch nearby events"
        )

    return {
        "status": "success",
        "merchant": {
            "business_name": merchant.business_name,
            "city": merchant.city,
            "latitude": float(merchant.latitude),
            "longitude": float(merchant.longitude)
        },
        "search_radius_km": 10,
        "events_found": len(events),
        "events": events
    }
@app.get("/api/radar/weather")
def get_weather(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == current_user.merchant_id)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant not found"
        )

    if not merchant.latitude or not merchant.longitude:
        raise HTTPException(
            status_code=400,
            detail="Merchant location is not configured"
        )

    weather = get_current_weather(
        float(merchant.latitude),
        float(merchant.longitude)
    )

    return {
        "status": "success",
        "merchant": {
            "business_name": merchant.business_name,
            "city": merchant.city,
            "latitude": float(merchant.latitude),
            "longitude": float(merchant.longitude)
        },
        "weather": weather
    }
@app.get("/api/agents/demand-radar")
def run_demand_radar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    return demand_radar.analyze(
        db=db,
        merchant_id=current_user.merchant_id
    )
# --------------------------------------------------
# OFFER + GUARDRAIL EVALUATION
# --------------------------------------------------

class OfferEvaluationRequest(BaseModel):
    mission_goal: str


@app.post("/api/missions/evaluate-offer")
def evaluate_offer(
    request: OfferEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ----------------------------------------
    # 1. GET LOCAL COMMERCE SIGNALS
    # ----------------------------------------

    merchant = (
        db.query(Merchant)
        .filter(
            Merchant.id == current_user.merchant_id
        )
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant not found"
        )

    if not merchant.latitude or not merchant.longitude:
        raise HTTPException(
            status_code=400,
            detail="Merchant location is not configured"
        )

    latitude = float(merchant.latitude)
    longitude = float(merchant.longitude)

    # Weather
    weather = get_current_weather(
        latitude,
        longitude
    )

    # Events
    try:
        events = get_nearby_events(
            latitude=latitude,
            longitude=longitude,
            radius_km=10,
            limit=10
        )
    except requests.RequestException:
        events = []

    # ----------------------------------------
    # 2. DEMAND RADAR
    # ----------------------------------------

    demand_result = demand_radar.analyze(
        db=db,
        merchant_id=current_user.merchant_id
    )

    products = demand_result.get(
        "products",
        []
    )

    # ----------------------------------------
    # 3. OPPORTUNITY ENGINE
    # ----------------------------------------

    opportunity_result = generate_opportunities(
        weather=weather,
        events=events,
        products=products
    )

    candidates = opportunity_result.get(
        "promotion_candidates",
        []
    )

    if not candidates:
        return {
            "status": "NO_OFFER",
            "message": (
                "No eligible product was found "
                "for promotion."
            ),
            "opportunity_engine": opportunity_result
        }

    # Highest-ranked candidate
    best_product = candidates[0]

    # ----------------------------------------
    # 4. GET PRODUCT ECONOMICS
    # ----------------------------------------

    economics = (
        db.query(ProductEconomics)
        .filter(
            ProductEconomics.merchant_id
            == current_user.merchant_id,
            ProductEconomics.product_id
            == best_product["product_id"]
        )
        .first()
    )

    if not economics:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": (
                "Pricing information is missing "
                "for the selected product."
            ),
            "selected_product": best_product
        }

    # Add economics to product
    product_for_offer = {
        **best_product,

        "selling_price": economics.selling_price,

        "cost_price": economics.cost_price,

        "max_discount_percentage":
            economics.max_discount_percentage
    }

    # ----------------------------------------
    # 5. OFFER AGENT
    # ----------------------------------------

    offer_result = generate_offer(
        mission_goal=request.mission_goal,
        product=product_for_offer,

        weather_signal=
            opportunity_result["signals"].get(
                "weather"
            ),

        event_signal=
            opportunity_result["signals"].get(
                "events"
            )
    )

    # ----------------------------------------
    # 6. GUARDRAIL ENGINE
    # ----------------------------------------

    guardrail_result = evaluate_offer_guardrails(
        offer_result=offer_result,

        budget_limit=5000,

        max_discount_percentage=
            economics.max_discount_percentage,

        minimum_margin_percentage=10,

        approval_required=True
    )

    # ----------------------------------------
    # 7. FINAL RESPONSE
    # ----------------------------------------

    return {
        "status": "success",

        "mission": {
            "goal": request.mission_goal
        },

        "selected_product": best_product,

        "offer": offer_result,

        "guardrails": guardrail_result,

        "next_step": (
            "Send to Approval Center"
            if guardrail_result["decision"]
            == "request_approval"
            else guardrail_result["decision"]
        )
    }
@app.post("/api/products/economics/upload")
def upload_product_economics(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    try:
        contents = file.file.read()

        df = pd.read_csv(
        io.BytesIO(contents),
        sep=None,
        engine="python"
        )
        df.columns = df.columns.str.strip().str.upper()
        print("CSV Columns:", df.columns.tolist())
        required_columns = [
            "PRODUCT_ID",
            "PRODUCT_NAME",
            "SELLING_PRICE",
            "COST_PRICE",
            "MAX_DISCOUNT_PERCENTAGE"
        ]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {missing}"
            )

        count = 0

        for _, row in df.iterrows():

            product_id = str(row["PRODUCT_ID"])

            existing = (
                db.query(ProductEconomics)
                .filter(
                    ProductEconomics.merchant_id
                    == current_user.merchant_id,
                    ProductEconomics.product_id
                    == product_id
                )
                .first()
            )

            if existing:
                existing.selling_price = float(
                    row["SELLING_PRICE"]
                )
                existing.cost_price = float(
                    row["COST_PRICE"]
                )
                existing.max_discount_percentage = float(
                    row["MAX_DISCOUNT_PERCENTAGE"]
                )

            else:
                economics = ProductEconomics(
                    merchant_id=current_user.merchant_id,
                    product_id=product_id,
                    selling_price=float(
                        row["SELLING_PRICE"]
                    ),
                    cost_price=float(
                        row["COST_PRICE"]
                    ),
                    max_discount_percentage=float(
                        row["MAX_DISCOUNT_PERCENTAGE"]
                    )
                )

                db.add(economics)

            count += 1

        db.commit()

        return {
            "status": "success",
            "message": "Product economics uploaded successfully",
            "products_updated": count
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# --------------------------------------------------
# CREATE MISSION
# --------------------------------------------------

@app.post(
    "/api/missions",
    response_model=MissionResponse
)
def create_mission(
    request: MissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ----------------------------------------
    # 1. ANALYZE MERCHANT GOAL
    # ----------------------------------------

    plan = goal_planner.analyze_goal(
        request.goal
    )

    # ----------------------------------------
    # 2. NO FAKE CURRENT REVENUE
    # ----------------------------------------

    # We currently do not have a live transaction feed.
    # Therefore, do not invent today's revenue.
    current_revenue = None

    # ----------------------------------------
    # 3. REVENUE GAP
    # ----------------------------------------

    revenue_gap = None

    # We can only calculate a real revenue gap
    # when live/current revenue is available.
    if (
        plan["target"] is not None
        and current_revenue is not None
    ):
        revenue_gap = max(
            plan["target"] - current_revenue,
            0
        )

    # ----------------------------------------
    # 4. CREATE MISSION
    # ----------------------------------------

    mission = {
        "goal": plan["original_goal"],
        "goal_type": plan["goal_type"],
        "target": plan["target"],
        "deadline": plan["deadline"],
        "priority": plan["priority"],
        "current_revenue": current_revenue,
        "revenue_gap": revenue_gap,
        "status": "running",
        "action_plan": plan["action_plan"]
    }

    return mission
# --------------------------------------------------
# CSV UPLOAD
# --------------------------------------------------
@app.post("/api/ml/train-demand-model")
def train_demand_model(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    rows = (
        db.query(ProductData)
        .filter(
            ProductData.merchant_id == current_user.merchant_id
        )
        .order_by(
            ProductData.product_id,
            ProductData.month
        )
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=400,
            detail="No merchant data available. Upload CSV first."
        )

    metrics = demand_model.train(rows)

    return {
        "message": "Demand forecasting model trained successfully",
        "merchant_id": current_user.merchant_id,
        "model": "Random Forest Regressor",
        "metrics": metrics
    }
@app.put("/api/merchant/location")
def update_merchant_location(
    location: MerchantLocationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == current_user.merchant_id)
        .first()
    )

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant not found"
        )

    merchant.city = location.city
    merchant.latitude = str(location.latitude)
    merchant.longitude = str(location.longitude)

    db.commit()
    db.refresh(merchant)

    return {
        "message": "Merchant location updated successfully",
        "merchant": {
            "merchant_id": merchant.merchant_id,
            "business_name": merchant.business_name,
            "city": merchant.city,
            "latitude": float(merchant.latitude),
            "longitude": float(merchant.longitude)
        }
    }
@app.post("/api/data/upload")
async def upload_csv(

    file: UploadFile = File(...),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)

):

    # Check file type
    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )


    # Create upload directory
    import os

    os.makedirs(
        "data/uploads",
        exist_ok=True
    )


    # Save uploaded file
    upload_path = (
        f"data/uploads/{file.filename}"
    )


    contents = await file.read()


    with open(
        upload_path,
        "wb"
    ) as buffer:

        buffer.write(contents)


    # Process CSV
    result = process_csv(
        upload_path
    )


    # Validation failed
    if not result["success"]:

        raise HTTPException(

            status_code=400,

            detail={

                "errors": result["errors"],

                "warnings": result.get(
                    "warnings",
                    []
                )

            }

        )


    # Save merchant-specific data
    rows_saved = save_product_data(

        db=db,

        merchant_id=current_user.merchant_id,

        df=result["data"]

    )


    return {

        "message": "CSV uploaded successfully",

        "filename": file.filename,

        "rows_processed": result["row_count"],

        "rows_saved": rows_saved,

        "detected_columns": result[
            "detected_columns"
        ],

        "warnings": result["warnings"]

    }


# --------------------------------------------------
# DATA SUMMARY
# --------------------------------------------------

@app.get("/api/data/summary")
def get_data_summary(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)

):

    total_rows = (

        db.query(ProductData)

        .filter(
            ProductData.merchant_id
            == current_user.merchant_id
        )

        .count()

    )


    unique_products = (

        db.query(

            func.count(

                func.distinct(
                    ProductData.product_id
                )

            )

        )

        .filter(

            ProductData.merchant_id
            == current_user.merchant_id

        )

        .scalar()

    )


    total_units = (

        db.query(

            func.coalesce(

                func.sum(
                    ProductData.unit_sales
                ),

                0

            )

        )

        .filter(

            ProductData.merchant_id
            == current_user.merchant_id

        )

        .scalar()

    )


    total_inventory = (

        db.query(

            func.coalesce(

                func.sum(
                    ProductData.quantity_on_hand
                ),

                0

            )

        )

        .filter(

            ProductData.merchant_id
            == current_user.merchant_id

        )

        .scalar()

    )


    return {

        "total_rows": total_rows,

        "unique_products": unique_products,

        "total_units_sold": int(
            total_units or 0
        ),

        "total_inventory": int(
            total_inventory or 0
        )

    }


# --------------------------------------------------
# PRODUCTS
# --------------------------------------------------

@app.get("/api/data/products")
def get_products(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)

):

    products = (

        db.query(ProductData)

        .filter(

            ProductData.merchant_id
            == current_user.merchant_id

        )

        .all()

    )


    return [

        {

            "product_id": product.product_id,

            "product_name": product.product_name,

            "month": product.month,

            "unit_sales": product.unit_sales,

            "supply_time": product.supply_time,

            "quantity_on_hand":
                product.quantity_on_hand

        }

        for product in products

    ]
# --------------------------------------------------
# HISTORICAL SALES
# --------------------------------------------------

@app.get("/api/data/sales-history")
def get_sales_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            ProductData.month,
            func.sum(ProductData.unit_sales).label("total_units")
        )
        .filter(
            ProductData.merchant_id == current_user.merchant_id
        )
        .group_by(ProductData.month)
        .order_by(ProductData.month)
        .all()
    )

    return [
        {
            "month": str(row.month),
            "total_units": int(row.total_units or 0)
        }
        for row in rows
    ]
# --------------------------------------------------
# AGENT ACTIVITY
# --------------------------------------------------

@app.get("/api/agents/activity")
def get_agent_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # -------------------------
    # 1. Demand Radar
    # -------------------------
    demand_result = demand_radar.analyze(
        db=db,
        merchant_id=current_user.merchant_id
    )

    products = demand_result.get("products", [])

    demand_reason = "No product analysis available."

    if products:
        top_product = products[0]

        demand_reason = (
            f"{top_product.get('product_name', 'Product')} identified with "
            f"{top_product.get('stock_days', 0):.1f} days of stock coverage. "
            f"Predicted demand: "
            f"{top_product.get('predicted_demand', 0):.0f} units."
        )

    # -------------------------
    # 2. Merchant context
    # -------------------------
    merchant = (
        db.query(Merchant)
        .filter(Merchant.id == current_user.merchant_id)
        .first()
    )

    weather = None
    events = []

    opportunity_status = "Waiting"
    opportunity_reason = "Waiting for contextual analysis."

    if merchant and merchant.latitude and merchant.longitude:

        try:
            weather = get_current_weather(
                float(merchant.latitude),
                float(merchant.longitude)
            )

            try:
                events = get_nearby_events(
                    latitude=float(merchant.latitude),
                    longitude=float(merchant.longitude),
                    radius_km=10,
                    limit=10
                )
            except requests.RequestException:
                events = []

            # -------------------------
            # 3. Opportunity Engine
            # -------------------------
            opportunity_result = generate_opportunities(
                weather=weather,
                events=events,
                products=products
            )

            candidates = opportunity_result.get(
                "promotion_candidates",
                []
            )

            if candidates:

                best = candidates[0]

                opportunity_status = "Completed"

                opportunity_reason = (
                    f"{best.get('product_name', 'Product')} selected as "
                    f"a promotion candidate with opportunity score "
                    f"{best.get('opportunity_score', 0)}."
                )

            else:

                opportunity_status = "Completed"
                opportunity_reason = (
                    "No promotion candidate identified under the "
                    "current inventory and business rules."
                )

        except Exception as e:

            print("Agent activity context error:", e)

    # -------------------------
    # 4. Return agent activity
    # -------------------------
    return {
        "status": "success",

        "agents": [

            {
                "name": "Goal Planner",
                "status": "Ready",
                "description":
                    "Converts merchant goals into structured missions.",
                "reasoning":
                    "Waiting for a new merchant mission."
            },

            {
                "name": "Demand Radar",
                "status":
                    "Completed" if products else "Waiting",
                "description":
                    "Analyzes historical sales and inventory.",
                "reasoning":
                    demand_reason
            },

            {
                "name": "Opportunity Engine",
                "status":
                    opportunity_status,
                "description":
                    "Identifies actionable commerce opportunities.",
                "reasoning":
                    opportunity_reason
            },

            {
                "name": "Offer Agent",
                "status": "Ready",
                "description":
                    "Generates offers using product economics.",
                "reasoning":
                    "Offer generation starts after an opportunity is selected."
            },

            {
                "name": "Campaign Agent",
                "status": "Waiting",
                "description":
                    "Prepares campaigns after an opportunity is approved.",
                "reasoning":
                    "Waiting for merchant approval."
            }

        ]
    }
class ApprovalRequest(BaseModel):
    product_id: str
    proposed_price: float
    discount_percentage: float
    decision: str


@app.post("/api/missions/approval")
def approve_mission_action(
    request: ApprovalRequest,
    current_user: User = Depends(get_current_user)
):
    if request.decision not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid approval decision"
        )

    return {
        "status": "success",
        "decision": request.decision,
        "product_id": request.product_id,
        "proposed_price": request.proposed_price,
        "discount_percentage": request.discount_percentage,
        "execution_status":
            "approved"
            if request.decision == "approved"
            else "rejected"
    }