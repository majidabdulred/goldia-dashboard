from datetime import timedelta, UTC, datetime
import humanize
from aiocache import cached, SimpleMemoryCache
from pymongo import DESCENDING
import pandas as pd

from database.client import get_database

db_logs = get_database()

mapping = {
    "DOWNLOAD_MASTERFILE": {"latest_time": timedelta(days=1), "col": "download_price_files",
                                   "query": {"shop": "MASTERFILE"}, "label": "Last 52544 files downloaded",
                                   "title": "Latest Masterfile"},
           "DOWNLOAD_SHOPIFY_US": {"latest_time": timedelta(days=1), "col": "download_price_files",
                                   "query": {"shop": "SHOPIFY_US"}, "label": "Variant file", "title": "Shopify US"},
           "DOWNLOAD_SHOPIFY_AU": {"latest_time": timedelta(days=1), "col": "download_price_files",
                                   "query": {"shop": "SHOPIFY_AU"}, "label": "Variant file", "title": "Shopify AU"},
           "DOWNLOAD_SHOPIFY_CA": {"latest_time": timedelta(days=1), "col": "download_price_files",
                                   "query": {"shop": "SHOPIFY_CA"}, "label": "Variant file", "title": "Shopify CA"},
           "DOWNLOAD_SHOPIFY_UK": {"latest_time": timedelta(days=1), "col": "download_price_files",
                                   "query": {"shop": "SHOPIFY_UK"}, "label": "Variant file", "title": "Shopify UK"},
           "DOWNLOAD_AMAZON_AU": {"latest_time": timedelta(days=1), "col": "download_price_files",
                                  "query": {"shop": "AMAZON_AU"}, "label": "Variant file", "title": "Amazon AU"},
           "DOWNLOAD_AMAZON_US": {"latest_time": timedelta(days=1), "col": "download_price_files",
                                  "query": {"shop": "AMAZON_US"}, "label": "Variant file", "title": "Amazon US"},

           "PRICE_UPDATE_AMAZON_US": {"latest_time": timedelta(days=1), "col": "update_amazon",
                                      "query": {"shop": "AMAZON_US"}, "label": "Last Price and inventory update",
                                      "title": "Amazon US Price & Quantity"},

           "PRICE_UPDATE_AMAZON_AU": {"latest_time": timedelta(days=1), "col": "update_amazon",
                                      "query": {"shop": "AMAZON_AU"}, "label": "Last Price and inventory update",
                                      "title": "Amazon AU Price & Quantity"},

            "PRICE_UPDATE_SHOPIFY_US": {"latest_time": timedelta(days=1), "col": "update_shopify",
                                      "query": {"shop": "SHOPIFY_US","prices":True}, "label": "Last price update",
                                          "title": "Shopify US Price"},

            "PRICE_UPDATE_SHOPIFY_AU": {"latest_time": timedelta(days=1), "col": "update_shopify",
                                      "query": {"shop": "SHOPIFY_AU","prices":True}, "label": "Last price update",
                                      "title": "Shopify AU Price"},

            "PRICE_UPDATE_SHOPIFY_CA": {"latest_time": timedelta(days=1), "col": "update_shopify",
                                      "query": {"shop": "SHOPIFY_CA","prices":True}, "label": "Last price update",
                                      "title": "Shopify CA Price"},

            "PRICE_UPDATE_SHOPIFY_UK": {"latest_time": timedelta(days=1), "col": "update_shopify",
                                      "query": {"shop": "SHOPIFY_UK","prices":True}, "label": "Last price update",
                                      "title": "Shopify UK Price"},

            "INVENTORY_UPDATE_SHOPIFY_US": {"latest_time": timedelta(days=1), "col": "update_shopify",
                                      "query": {"shop": "SHOPIFY_US","inventory":True}, "label": "Last inventory update",
                                      "title": "Shopify US Inventory"},

            "INVENTORY_UPDATE_SHOPIFY_AU": {"latest_time": timedelta(days=1), "col": "update_shopify",
                                      "query": {"shop": "SHOPIFY_AU","inventory":True}, "label": "Last inventory update",
                                      "title": "Shopify AU Inventory"},

            "INVENTORY_UPDATE_SHOPIFY_CA": {"latest_time": timedelta(days=1), "col": "update_shopify",
                                      "query": {"shop": "SHOPIFY_CA","inventory":True}, "label": "Last inventory update",
                                      "title": "Shopify CA Inventory"},

            "INVENTORY_UPDATE_SHOPIFY_UK": {"latest_time": timedelta(days=1), "col": "update_shopify",
                                      "query": {"shop": "SHOPIFY_UK","inventory":True}, "label": "Last inventory update",
                                      "title": "Shopify UK Inventory"},

           "UPDATE_TRACKING_NUMBER_SHIPSTATION": {"latest_time": timedelta(hours=6), "col": "update_tracking_number",
                                                  "query": {}, "label": "Tracking number was updated to shipstation",
                                                  "title": "Shipping Shipstation"},

           "UPDATE_TRACKING_NUMBER_WALMART": {"latest_time": timedelta(hours=6), "col": "walmart_update_tracking_number",
                                              "query": {}, "label": "Updating tracking number to walmart",
                                              "title": "Shipping Walmart"},

           "ORDER_TAGGING": {"latest_time": timedelta(hours=6), "col": "order_tagging",
                             "query": {}, "label": "Orders Tagging after processing", "title": "Tagging Orders"},

           "UPLOAD_ORDERS": {"latest_time": timedelta(hours=6), "col": "upload_orders",
                             "query": {}, "label": "Orders uploading to ftp", "title": "Uploading Orders"},

           }

@cached(ttl=60, cache=SimpleMemoryCache)
async def _get_document(col, query, length):
    cursor = db_logs.get_collection(col).find(
        query
    ).sort("createdAt", DESCENDING)

    results = await cursor.to_list(length=length)
    return results


async def get_last_run(method):

    data = mapping[method]

    res = await _get_document(data["col"], data["query"], 1)
    if res is None:
        return "Never", "inverse"

    created_at = res[0]["createdAt"].replace(tzinfo=UTC)
    now = datetime.now(UTC)

    color = "normal"
    if (now - created_at) > data["latest_time"]:
        color = "inverse"

    return method,humanize.naturaltime(now - created_at), color



async def get_uploaded_orders():
    ors = await _get_document("upload_orders", {"orders": {"$ne": []}}, length=100)
    orders = []
    for i in ors:
        ors = i["orders"]
        for k in range(len(ors)):
            ors[k]["createdAt"] = i["createdAt"]
        orders.extend(i["orders"])
    orders = [{"createdAt": humanize.naturaltime(order["createdAt"]),
               "Order Number": order["order_number"],
               "sku": order["sku"], "name": order["name"],
               "quantity": order["quantity"],
               "paid": order["amount"]}
              for order in orders]
    return pd.DataFrame(orders)

async def get_tracking_updated_orders():
    ors = await _get_document("update_tracking_number", {"orders": {"$ne": []}}, length=100)
    orders = []
    for i in ors:
        ors = i["orders"]
        for k in range(len(ors)):
            ors[k]["createdAt"] = i["createdAt"]
        orders.extend(i["orders"])
    orders = [{"createdAt": humanize.naturaltime(order["createdAt"]),
               "Order Number": order["poNumber"],
               "Order ID": order["orderId"],
               "Carrier": order["carrierName"],
               "Tracking Number": order["trackingNumber"]}
              for order in orders]
    return pd.DataFrame(orders)

async def shopify_updates():
    updates = await _get_document("update_shopify", {}, length=100)
    df = pd.DataFrame(updates)
    df["createdAt"] = df.createdAt.apply(lambda x: humanize.naturaltime(x))
    df = df[["createdAt", "shop", "products", "prices", "inventory"]]
    return df
