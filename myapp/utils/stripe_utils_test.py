
# -*- coding: utf-8 -*-

import stripe
import time
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from dotenv import load_dotenv
load_dotenv()


# =====================================================
# STRIPE CONFIG
# =====================================================
STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY")

SUCCESS_URL = "https://81a9832a2b3c.ngrok-free.app/payment/success?session_id={CHECKOUT_SESSION_ID}"
# CANCEL_URL = "https://example.com/payment/cancel"

DEFAULT_SESSION_EXPIRY_HOURS = 24

stripe.api_key = STRIPE_API_KEY

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def dollars_to_cents(amount: float) -> int:
    rounded = Decimal(str(amount)).quantize(
        Decimal("0.00"),
        rounding=ROUND_HALF_UP
    )
    return int(rounded * 100)


def cents_to_dollars(cents: int) -> Decimal:
    return (Decimal(cents) / Decimal("100")).quantize(Decimal("0.00"))


def calculate_deposit_cents(
    total_amount_dollars: float,
    deposit_percentage: Optional[float] = None,
    minimum_deposit_amount_dollars: Optional[float] = None,
) -> int:
    total_cents = dollars_to_cents(total_amount_dollars)

    if deposit_percentage is not None:
        if not (0 < deposit_percentage <= 100):
            raise ValueError("deposit_percentage must be between 0 and 100")
        deposit_cents = int(total_cents * (deposit_percentage / 100))

    elif minimum_deposit_amount_dollars is not None:
        deposit_cents = dollars_to_cents(minimum_deposit_amount_dollars)

    else:
        raise ValueError(
            "Either deposit_percentage or minimum_deposit_amount_dollars is required"
        )

    if deposit_cents <= 0:
        raise ValueError("Deposit amount must be greater than zero")

    return min(deposit_cents, total_cents)

# =====================================================
# STRIPE LINE ITEM
# =====================================================
def create_stripe_payment_line(payload: dict) -> dict:
    if "total_amount_dollars" not in payload:
        raise ValueError("total_amount_dollars missing")

    if "booking_id" not in payload:
        raise ValueError("booking_id missing")

    deposit_cents = calculate_deposit_cents(
        total_amount_dollars=payload["total_amount_dollars"],
        deposit_percentage=payload.get("deposit_percentage"),
        minimum_deposit_amount_dollars=payload.get("minimum_deposit_amount_dollars"),
    )

    # IMPORTANT: handle None correctly
    product_data = payload.get("product_data") or {
        "name": "Booking Deposit",
        "description": f"Deposit for booking {payload['booking_id']}",
    }

    return {
        "price_data": {
            "currency": payload.get("currency", "usd"),
            "product_data": product_data,
            "unit_amount": deposit_cents,
        },
        "quantity": 1,
    }

# =====================================================
# STRIPE CHECKOUT SESSION
# =====================================================
def create_stripe_checkout_session(payload: dict):
    payment_line = create_stripe_payment_line(payload)

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        expires_at=int(time.time()) + (DEFAULT_SESSION_EXPIRY_HOURS * 60 * 60),
        line_items=[payment_line],
        client_reference_id=payload["booking_id"],
        metadata={
            "booking_id": payload["booking_id"],
            "payment_type": "deposit",
            "deposit_amount_cents": str(
                payment_line["price_data"]["unit_amount"]
            ),
        },
        success_url=payload.get("success_url", SUCCESS_URL),
        # cancel_url=payload.get("cancel_url", CANCEL_URL),
    )

    return session

# =====================================================
# CONVENIENCE FUNCTION
# =====================================================
def create_deposit_payment_link(
    total_amount_dollars: float,
    booking_id: str,
    deposit_percentage: Optional[float] = None,
    minimum_deposit_amount_dollars: Optional[float] = None,
    product_data: Optional[dict] = None,
) -> str:

    payload = {
        "total_amount_dollars": total_amount_dollars,
        "booking_id": booking_id,
        "deposit_percentage": deposit_percentage,
        "minimum_deposit_amount_dollars": minimum_deposit_amount_dollars,
        "product_data": product_data,
    }

    session = create_stripe_checkout_session(payload)
    return session.url

# # =====================================================
# # TEST RUN
# # # =====================================================
# # if __name__ == "__main__":
# #     print("=" * 60)
# #     print("CREATING STRIPE DEPOSIT SESSION")
# #     print("=" * 60)

# #     # payment_url = create_deposit_payment_link(
# #     #     total_amount_dollars=744.50,
# #     #     booking_id="TEST99",
# #     #     deposit_percentage=50.0,
# #     # )


# #     payment_url = create_deposit_payment_link(
# #         total_amount_dollars=744.50,
# #         booking_id="TEST99",
# #         deposit_percentage=None,
# #         minimum_deposit_amount_dollars=200.0,
# #         product_data={
# #             "name": "Epic Party Jump Package",
# #             "description": (
# #                 "Epic Party Jump Package (Qty: 1, $340.00) | "
# #                 "Epic Party Additional Jumper (Qty: 10, $34.00) | "
# #                 "Pizza - Pepperoni (Qty: 1, $0.00) | "
# #                 "Pizza - Cheese (Qty: 1, $0.00) | "
# #                 "Pizza - Sausage (Qty: 2, $0.00) | "
# #                 "Party Beverage - Pepsi (Qty: 1, $0.00) | "
# #                 "Party Beverage - Starry (Qty: 2, $0.00) | "
# #                 "Chicken Strip Tray (Qty: 1, $37.99) | "
# #                 "Party Beverage - Diet Pepsi (Qty: 1, $0.00) | "
# #                 "Nacho Tray (Qty: 1, $27.99)"
# #             ),
# #             "images": [
# #                 "https://d1wqzb5bdbcre6.cloudfront.net/5b4565d6c26dffaed3e147ce52296994ac0acb313ee9b1d97bf5a1295446bd57/68747470733a2f2f63646e2e726f6c6c65726469676974616c2e636f6d2f696d6167652f4b476a4474646a4130454b6233314f505567343065772e6a7065/6d65726368616e745f69643d616363745f3144737230764854336d613262744e4426636c69656e743d5041594d454e545f50414745"
# #             ],
# #         }
# #     )


# #     print("✅ Stripe Checkout URL created:")
# #     print(payment_url)







# # -*- coding: utf-8 -*-

# import time
# from decimal import Decimal, ROUND_HALF_UP
# from typing import Optional
# import stripe
# import asyncio

# # =====================================================
# # STRIPE CONFIG
# # =====================================================

# SUCCESS_URL = "https://example.com/payment/success?session_id={CHECKOUT_SESSION_ID}"
# CANCEL_URL = "https://example.com/payment/cancel"

# DEFAULT_SESSION_EXPIRY_HOURS = 24

# stripe.api_key = STRIPE_API_KEY

# # =====================================================
# # HELPER FUNCTIONS
# # =====================================================
# def dollars_to_cents(amount: float) -> int:
#     rounded = Decimal(str(amount)).quantize(
#         Decimal("0.00"),
#         rounding=ROUND_HALF_UP
#     )
#     return int(rounded * 100)


# def cents_to_dollars(cents: int) -> Decimal:
#     return (Decimal(cents) / Decimal("100")).quantize(Decimal("0.00"))


# def calculate_deposit_cents(
#     total_amount_dollars: float,
#     deposit_percentage: Optional[float] = None,
#     minimum_deposit_amount_dollars: Optional[float] = None,
# ) -> int:
#     total_cents = dollars_to_cents(total_amount_dollars)

#     if deposit_percentage is not None:
#         if not (0 < deposit_percentage <= 100):
#             raise ValueError("deposit_percentage must be between 0 and 100")
#         deposit_cents = int(total_cents * (deposit_percentage / 100))

#     elif minimum_deposit_amount_dollars is not None:
#         deposit_cents = dollars_to_cents(minimum_deposit_amount_dollars)

#     else:
#         raise ValueError(
#             "Either deposit_percentage or minimum_deposit_amount_dollars is required"
#         )

#     if deposit_cents <= 0:
#         raise ValueError("Deposit amount must be greater than zero")

#     return min(deposit_cents, total_cents)

# # =====================================================
# # STRIPE LINE ITEM
# # =====================================================
# def create_stripe_payment_line(payload: dict) -> dict:
#     if "total_amount_dollars" not in payload:
#         raise ValueError("total_amount_dollars missing")

#     if "booking_id" not in payload:
#         raise ValueError("booking_id missing")

#     deposit_cents = calculate_deposit_cents(
#         total_amount_dollars=payload["total_amount_dollars"],
#         deposit_percentage=payload.get("deposit_percentage"),
#         minimum_deposit_amount_dollars=payload.get("minimum_deposit_amount_dollars"),
#     )

#     product_data = payload.get("product_data") or {
#         "name": "Booking Deposit",
#         "description": f"Deposit for booking {payload['booking_id']}",
#     }

#     return {
#         "price_data": {
#             "currency": payload.get("currency", "usd"),
#             "product_data": product_data,
#             "unit_amount": deposit_cents,
#         },
#         "quantity": 1,
#     }

# # =====================================================
# # STRIPE CHECKOUT SESSION (ASYNC)
# # =====================================================
# async def create_stripe_checkout_session(payload: dict):
#     payment_line = create_stripe_payment_line(payload)

#     # stripe.checkout.Session.create is normally sync, 
#     # but we can run it in a thread for async behavior
#     loop = asyncio.get_event_loop()
#     session = await loop.run_in_executor(
#         None,
#         lambda: stripe.checkout.Session.create(
#             mode="payment",
#             payment_method_types=["card"],
#             expires_at=int(time.time()) + (DEFAULT_SESSION_EXPIRY_HOURS * 60 * 60),
#             line_items=[payment_line],
#             client_reference_id=payload["booking_id"],
#             metadata={
#                 "booking_id": payload["booking_id"],
#                 "payment_type": "deposit",
#                 "deposit_amount_cents": str(payment_line["price_data"]["unit_amount"]),
#             },
#             success_url=payload.get("success_url", SUCCESS_URL),
#             cancel_url=payload.get("cancel_url", CANCEL_URL),
#         )
#     )

#     return session

# # =====================================================
# # CONVENIENCE FUNCTION (ASYNC)
# # =====================================================
# async def create_deposit_payment_link(
#     total_amount_dollars: float,
#     booking_id: str,
#     deposit_percentage: Optional[float] = None,
#     minimum_deposit_amount_dollars: Optional[float] = None,
#     product_data: Optional[dict] = None,
# ) -> str:

#     payload = {
#         "total_amount_dollars": total_amount_dollars,
#         "booking_id": booking_id,
#         "deposit_percentage": deposit_percentage,
#         "minimum_deposit_amount_dollars": minimum_deposit_amount_dollars,
#         "product_data": product_data,
#     }

#     session = await create_stripe_checkout_session(payload)
#     return session.url

# # =====================================================
# # TEST RUN
# # =====================================================
# if __name__ == "__main__":
#     print("=" * 60)
#     print("CREATING STRIPE DEPOSIT SESSION (ASYNC)")
#     print("=" * 60)

#     async def main():
#         payment_url = await create_deposit_payment_link(
#             total_amount_dollars=744.50,
#             booking_id="TEST99",
#             # deposit_percentage=50.0,
#             # minimum_deposit_amount_dollars=200.0,
#             product_data={
#                 "name": "Epic Party Jump Package",
#                 "description": (
#                     "Epic Party Jump Package (Qty: 1, $340.00) | "
#                     "Epic Party Additional Jumper (Qty: 10, $34.00) | "
#                     "Pizza - Pepperoni (Qty: 1, $0.00) | "
#                     "Pizza - Cheese (Qty: 1, $0.00) | "
#                     "Pizza - Sausage (Qty: 2, $0.00) | "
#                     "Party Beverage - Pepsi (Qty: 1, $0.00) | "
#                     "Party Beverage - Starry (Qty: 2, $0.00) | "
#                     "Chicken Strip Tray (Qty: 1, $37.99) | "
#                     "Party Beverage - Diet Pepsi (Qty: 1, $0.00) | "
#                     "Nacho Tray (Qty: 1, $27.99)"
#                 ),
#                 "images": [
#                     "https://d1wqzb5bdbcre6.cloudfront.net/5b4565d6c26dffaed3e147ce52296994ac0acb313ee9b1d97bf5a1295446bd57/68747470733a2f2f63646e2e726f6c6c65726469676974616c2e636f6d/6d65726368616e745f69643d616363745f3144737230764854336d613262744e44"
#                 ],
#             }
#         )
#         print("✅ Stripe Checkout URL created:")
#         print(payment_url)

#     asyncio.run(main())
