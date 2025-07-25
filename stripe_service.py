from dotenv import load_dotenv

import stripe
import os

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_express_account(email: str):
    return stripe.Account.create(
        type="express",
        country="CA",
        email=email,
        capabilities={"transfers": {"requested": True}},
    )

def create_account_link(account_id: str, refresh_url: str, return_url: str):
    return stripe.AccountLink.create(  
        account=account_id,
        refresh_url=refresh_url,
        return_url=return_url,
        type="account_onboarding"
    )

def create_payment_intent(amount: int, currency: str, connected_account_id: str):
    return stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        application_fee_amount=int(amount * 0.1),  # 10% platform fee
        transfer_data={"destination": connected_account_id},
    )

def create_express_login_link(account_id: str):
    return stripe.Account.create_login_link(account_id)

def list_connected_accounts():
    return stripe.Account.list(limit=10)
