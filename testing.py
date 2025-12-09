import asyncio
from data_loading_short_prompt_v3 import *
import tracemalloc
tracemalloc.start()

TRANSFER_PHONE_NUMBER = "+1707215444"
MAX_RETRY_ATTEMPTS = 3
RETRY_INTERVAL_SECONDS = 30
# LOCATION = "Hamilton"
# SHEET_ID = "1vVqr2drEn9pg-DnEuBgETXGBUgH8zL33goD0Jfo-h4Q" # Ventura
# SHEET_ID = "115RCRCq8igg1LR4gWxzsCoYK1JOppe2Ut_431tvVcQI" # Ventura
SHEET_ID = "1PdeT6S5yQJQAIt9lJkhJxQOoZrantnsDIEaAHzvbC20" # columbia
SHEET_ID_MCDONOUGH = "1hr4b05B2ri65XM6hGr6tdSDSarKxyX_nCKVswsuNB8c" # Mcdonough
base_url = "https://app.rivette.ai/crmapi/v2.2/bot"
Auth_key = "MIIJKgIBAAKCAgEAqoQmo+3eejP6LzvUzZggeevGiS4lmKXDw06xOqe1u8AfJpf70wmybM0Dh1N65tNPMr+M2oibA0q4dtbW6lM1ptPlj7DHqjC7H8YWiqv0wSVNsOpjobndUDdrZufvouo3eqQ4jIKiAsV7dQnNi1R7lxLGTx5m7jL121l6qV7Ckr24oHZLGBbVNcPNsFmVTTt"
client_id = 39
# ADDRESS = """
# Address: 17 Quakerbridge Plaza Unit B, Hamilton Township, New Jersey
# Nearest Location: TD Bank
# """

# print(special_hours)
async def extract_package_ids(roller_birthday_party_packages):
  roller_product_ids = []
  for package in roller_birthday_party_packages:
      package_search_id = package.get("Pid", "")
      if package_search_id:
          roller_product_ids.append(package_search_id)
      package_sub_products = package.get("products", [])
      for sub_product in package_sub_products:
          sub_product_id = sub_product.get("id", "")
          if sub_product_id:
            roller_product_ids.append(sub_product_id)
  return roller_product_ids

async def extract_other_products_ids(product_data):
  roller_product_ids = []
  for product in product_data:
      product_booking_id = product.get("Pid", "")
      if product_booking_id:
          roller_product_ids.append(product_booking_id)
      
  return roller_product_ids
async def get_roller_products(client_id):


    roller_product_ids = []
    ## url : https://test.rivette.ai/crmapi/v2.2/bot/customer/search_roller_customers?client_id=1&search=Addison


    url = f"{base_url}/get_products"


    headers = {
        "Accept": "application/json",
        "x-authorization": Auth_key,


    }
    params = {
        "client_id": client_id, ## for elk grove
        # "search": f"{customer_phone}" ## search by name,search=name or phone or email or customer id (roller customer id)
    }


    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(url, headers=headers, params=params) as res:
            if res.status == 200:
                response = await res.json()
                if response["status"] == "success":
                    response_dict = response["data"]

                    # Extract product categories
                    
                    roller_birthday_party_packages = response_dict.get("package", [])         
                    roller_food_items = response_dict.get("food_items", [])
                    # pprint.pprint(roller_food_items,indent=4)
                    roller_party_trays = response_dict.get("party_trays", [])
                    roller_drinks = response_dict.get("drinks", [])
                    product_ids_lists = await asyncio.gather(
                        extract_package_ids(roller_birthday_party_packages),
                        extract_other_products_ids(roller_food_items),
                       extract_other_products_ids(roller_party_trays),
                        extract_other_products_ids(roller_drinks)
                    )
                    for product_ids_list in product_ids_lists:
                        roller_product_ids.extend(product_ids_list)
                    return roller_product_ids
                else:
                    return []
            else:
                return []

async def test_load_data():
    for _ in range(1):
        try:
            roller_product_ids = await get_roller_products(39)
            await load_data(caller_number="123",sheet_id = SHEET_ID_MCDONOUGH,
                            skip_customer_details_in_prompt=False,customer_first_name="Saqib",
                            customer_last_name="Zia",
                            customer_email="saqib.zia@sybrid.com",is_edit_details=False,
                            edit_booking_details_tuple = (),roller_product_ids = roller_product_ids)
            # await load_data("",sheet_id = SHEET_ID)
            break 

        except BaseException as e:
            print(e)
            await asyncio.sleep(1)


asyncio.run(test_load_data())






