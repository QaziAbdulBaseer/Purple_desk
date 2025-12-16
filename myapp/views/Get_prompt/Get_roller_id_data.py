



import aiohttp
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
PRODUCT_URL = os.environ.get("PRODUCT_URL")
AUTH_KEY = os.environ.get("AUTH_KEY")
# print("auth key is :" , AUTH_KEY)

if not all([BASE_URL, PRODUCT_URL, AUTH_KEY]):
    raise ValueError("BASE_URL, PRODUCT_URL, or AUTH_KEY not set in environment")

HEADERS = {
    "Accept": "application/json",
    "x-authorization": AUTH_KEY
}


async def search_roller_customer(customer_phone: str, client_id: int):
    """
    Search roller customer by phone
    Returns a dict with customer details or None
    """
    url = f"{PRODUCT_URL}/customer/search_roller_customers"
    params = {
        "client_id": client_id,
        "search": customer_phone
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, params=params) as res:
            if res.status != 200:
                print(f"Error: HTTP {res.status}")
                return None

            data = await res.json()
            if data.get("status") != "success":
                print("Error: API returned unsuccessful status")
                return None

            customers = data.get("data", [])
            if not customers:
                print("No customer found")
                return None

            customer = customers[0]
            return {
                "customer_id": customer.get("customerId"),
                "first_name": customer.get("firstName"),
                "last_name": customer.get("lastName"),
                "email": customer.get("email")
            }

                                                                                                                                                                                                                                                                                                                                                                                                                        
# async def main():
#     client_id = 1
#     phone_to_search = "3359102086"  # Your customer phone number

#     customer = await search_roller_customer(phone_to_search, client_id)

#     if customer:
#         print(f"Customer found: {customer}")
#     else:
#         print("Customer not found")


# if __name__ == "__main__":
#     asyncio.run(main())
