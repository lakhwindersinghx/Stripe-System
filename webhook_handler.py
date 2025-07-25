import os
import stripe
from dotenv import load_dotenv
from fastapi import Request, HTTPException
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def handle_webhook(request: Request, payload: bytes, sig_header: str):
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")

    # 🚦 Handle specific event types
    if event["type"] == "account.updated":
        account = event["data"]["object"]
        if account["charges_enabled"]:
            print(f"[Webhook] Onboarding completed for {account['id']}")

    elif event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        print(f"[Webhook] Payment succeeded: {payment_intent['id']}")

    elif event["type"] == "payout.paid":
        payout = event["data"]["object"]
        print(f"[Webhook] Payout sent: {payout['id']}")
    elif event["type"] == "payout.paid":
        payout = event["data"]["object"]
        print(f"[Webhook] ✅ Payout sent: {payout['id']} to account: {payout['destination']}")    

    return {"status": "success"}
