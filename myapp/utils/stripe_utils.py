"""
Stripe payment utility functions for Purple Desk backend
"""

import os
import time
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any, Tuple
import stripe
from django.conf import settings

logger = logging.getLogger(__name__)

# Initialize Stripe with environment variables
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentUtils:
    """Utility class for Stripe payment operations"""
    
    @staticmethod
    def dollars_to_cents(amount: float) -> int:
        """
        Convert dollars to cents for Stripe (Stripe uses cents)
        
        Args:
            amount: Amount in dollars (float)
            
        Returns:
            Amount in cents (int)
        """
        try:
            rounded = Decimal(str(amount)).quantize(
                Decimal("0.00"),
                rounding=ROUND_HALF_UP
            )
            return int(rounded * 100)
        except Exception as e:
            logger.error(f"Error converting dollars to cents: {str(e)}")
            raise
    
    @staticmethod
    def cents_to_dollars(cents: int) -> Decimal:
        """
        Convert cents to dollars
        
        Args:
            cents: Amount in cents (int)
            
        Returns:
            Amount in dollars (Decimal)
        """
        try:
            return (Decimal(cents) / Decimal("100")).quantize(Decimal("0.00"))
        except Exception as e:
            logger.error(f"Error converting cents to dollars: {str(e)}")
            raise
    
    @staticmethod
    def calculate_deposit_cents(
        total_amount_dollars: float,
        deposit_percentage: Optional[float] = None,
        minimum_deposit_amount_dollars: Optional[float] = None,
    ) -> Tuple[int, float]:
        """
        Calculate deposit amount in cents
        
        Args:
            total_amount_dollars: Total booking amount in dollars
            deposit_percentage: Percentage of total for deposit
            minimum_deposit_amount_dollars: Minimum deposit amount in dollars
            
        Returns:
            Tuple of (deposit_cents, deposit_percentage_used)
        """
        total_cents = StripePaymentUtils.dollars_to_cents(total_amount_dollars)
        deposit_percentage_used = 0.0
        
        if deposit_percentage is not None:
            if not (0 < deposit_percentage <= 100):
                raise ValueError("deposit_percentage must be between 0 and 100")
            
            deposit_cents = int(round(total_cents * (deposit_percentage / 100)))
            deposit_percentage_used = deposit_percentage
            
        elif minimum_deposit_amount_dollars is not None:
            deposit_cents = StripePaymentUtils.dollars_to_cents(minimum_deposit_amount_dollars)
            if total_amount_dollars > 0:
                deposit_percentage_used = (deposit_cents / total_cents) * 100
        else:
            raise ValueError("Either deposit_percentage or minimum_deposit_amount_dollars must be provided")
        
        # Safety: deposit must not exceed total
        deposit_cents = min(deposit_cents, total_cents)
        
        return deposit_cents, deposit_percentage_used
    
    @staticmethod
    def create_payment_session(
        booking_id: str,
        booking_unique_id: str,
        total_amount_dollars: float,
        customer_email: str,
        customer_name: str,
        deposit_percentage: Optional[float] = None,
        minimum_deposit_amount_dollars: Optional[float] = None,
        product_name: str = "Booking Deposit",
        product_description: str = "",
        images: Optional[list] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create Stripe Checkout session for payment
        
        Args:
            booking_id: Internal booking ID
            booking_unique_id: Unique booking identifier
            total_amount_dollars: Total booking amount in dollars
            customer_email: Customer email
            customer_name: Customer full name
            deposit_percentage: Percentage for deposit calculation
            minimum_deposit_amount_dollars: Minimum deposit amount
            product_name: Product name for Stripe
            product_description: Product description for Stripe
            images: List of image URLs
            success_url: Custom success URL
            cancel_url: Custom cancel URL
            metadata: Additional metadata
            
        Returns:
            Dictionary with session details
        """
        try:
            # Calculate deposit
            deposit_cents, deposit_percentage_used = StripePaymentUtils.calculate_deposit_cents(
                total_amount_dollars=total_amount_dollars,
                deposit_percentage=deposit_percentage,
                minimum_deposit_amount_dollars=minimum_deposit_amount_dollars
            )
            
            # Prepare product description
            if not product_description:
                product_description = f"Booking ID: {booking_unique_id}"
            
            # Prepare images
            if not images:
                images = ["https://images.unsplash.com/photo-1511795409834-ef04bbd61622?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80"]
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "booking_id": booking_id,
                "booking_unique_id": booking_unique_id,
                "customer_email": customer_email,
                "customer_name": customer_name,
                "total_amount_dollars": str(total_amount_dollars),
                "deposit_percentage": str(deposit_percentage_used),
                "payment_type": "deposit" if deposit_percentage_used < 100 else "full"
            })
            
            # Prepare success and cancel URLs
            if not success_url:
                success_url = f"{settings.FRONTEND_BASE_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            
            if not cancel_url:
                cancel_url = f"{settings.FRONTEND_BASE_URL}/payment/cancel"
            
            # Create Stripe session
            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                expires_at=int(time.time()) + (24 * 60 * 60),  # 24 hours
                customer_email=customer_email,
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": product_name,
                                "description": product_description,
                                "images": images,
                            },
                            "unit_amount": deposit_cents,
                        },
                        "quantity": 1,
                    }
                ],
                client_reference_id=booking_unique_id,
                metadata=metadata,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            
            logger.info(f"Stripe session created for booking {booking_unique_id}: {session.id}")
            
            return {
                "success": True,
                "session_id": session.id,
                "payment_url": session.url,
                "expires_at": session.expires_at,
                "amount_cents": deposit_cents,
                "amount_dollars": deposit_cents / 100,
                "deposit_percentage": deposit_percentage_used,
                "metadata": metadata
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error creating payment session: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            logger.error(f"Error creating Stripe payment session: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
    
    @staticmethod
    def retrieve_session(session_id: str) -> Dict[str, Any]:
        """
        Retrieve Stripe session details
        
        Args:
            session_id: Stripe session ID
            
        Returns:
            Dictionary with session details
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            return {
                "success": True,
                "session_id": session.id,
                "payment_status": session.payment_status,
                "status": session.status,
                "customer_email": session.customer_email,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "metadata": session.metadata,
                "expires_at": session.expires_at,
                "url": session.url,
                "client_reference_id": session.client_reference_id
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error retrieving session: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            logger.error(f"Error retrieving Stripe session: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }

