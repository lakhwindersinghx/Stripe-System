from fastapi import FastAPI, Request
from fastapi import Header, HTTPException
from pydantic import BaseModel
from webhook_handler import handle_webhook
from fastapi.responses import JSONResponse
from stripe_service import *
from webhook_handler import handle_webhook
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting up...")
    for route in app.routes:
        print("Available routes:")
        print(f"{route.path} -> {getattr(route, 'name', 'N/A')}")
    yield  # Control passes to the app
    # Shutdown logic
    print("Shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,  # Changed to True for better compatibility
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create router for API endpoints
router = APIRouter()

class PaymentRequest(BaseModel):
    amount: int
    account_id: str

@app.get("/")
async def root():
    return {"message": "SO‑Pay Backend is running"}

@app.get("/accounts")
async def list_accounts():
    return list_connected_accounts()

# Define the connected-accounts endpoint on the router
@router.get("/connected-accounts")
def get_connected_accounts():
    try:
        accounts = list_connected_accounts()
        return {"accounts": accounts.data}
    except Exception as e:
        print(f"Error fetching connected accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch connected accounts")

@app.post("/create-payment-intent")
async def create_payment_endpoint(data: PaymentRequest):
    try:
        print("[Request] Creating PaymentIntent with:", data)
        intent = create_payment_intent(
            amount=data.amount * 100,  # Convert to cents
            currency="cad",
            connected_account_id=data.account_id,
        )
        return {"client_secret": intent.client_secret}
    except stripe.error.StripeError as e:
        print("[Stripe Error]", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("[Unhandled Error]", e)
        raise HTTPException(status_code=400, detail="Unhandled error occurred.")

@app.post("/onboard")
async def onboard_user(data: dict):
    email = data["email"]
    account = create_express_account(email)
    link = create_account_link(
        account.id,
        refresh_url=f"{os.getenv('DOMAIN')}/onboard",
        return_url=f"{os.getenv('DOMAIN')}/dashboard"
    )
    return {"url": link.url, "account_id": account.id}

@app.post("/pay")
async def create_payment(data: dict):
    amount = int(float(data["amount"]) * 100)
    account_id = data["account_id"]
    intent = create_payment_intent(amount, "cad", account_id)
    return {"client_secret": intent.client_secret}

@app.get("/dashboard-login/{account_id}")
async def get_dashboard_login(account_id: str):
    try:
        login_link = create_express_login_link(account_id)
        return {"url": login_link.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#simple webhook to listen to backend events
@app.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    payload = await request.body()
    try:
        return handle_webhook(request, payload, stripe_signature)
    except HTTPException as e:
        return JSONResponse(status_code=400, content={"error": str(e.detail)})

# Include the router with /api prefix
app.include_router(router, prefix="/api")

# Add a test endpoint to verify CORS
@app.get("/api/test-cors")
async def test_cors():
    return {"message": "CORS is working!", "timestamp": "2025-01-25"}
