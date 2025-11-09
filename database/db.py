from datetime import timedelta, UTC, datetime

import humanize
import streamlit as st
from pymongo import DESCENDING

from database.client import get_database

db_logs = get_database()

mapping = {"DOWNLOAD_MASTERFILE": {"latest_time": timedelta(days=1), "col": "download_price_files",
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
                                      "query": {"shop": "AMAZON_US"}, "label": "Last Price and Quantity update",
                                      "title": "Amazon US Price & Quantity"},
           "PRICE_UPDATE_AMAZON_AU": {"latest_time": timedelta(days=1), "col": "update_amazon",
                                      "query": {"shop": "AMAZON_AU"}, "label": "Last Price and Quantity update",
                                      "title": "Amazon AU Price & Quantity"},

           "UPDATE_TRACKING_NUMBER_SHIPSTATION": {"latest_time": timedelta(days=1), "col": "update_tracking_number",
                                                  "query": {}, "label": "Tracking number was updated to shipstation",
                                                  "title": "Shipping Shipstation"},

           "UPDATE_TRACKING_NUMBER_WALMART": {"latest_time": timedelta(days=1), "col": "walmart_update_tracking_number",
                                              "query": {}, "label": "Updating tracking number to walmart",
                                              "title": "Shipping Walmart"},

           "ORDER_TAGGING": {"latest_time": timedelta(days=1), "col": "order_tagging",
                             "query": {}, "label": "Orders Tagging after processing", "title": "Tagging Orders"},

           "UPLOAD_ORDERS": {"latest_time": timedelta(days=1), "col": "upload_orders",
                             "query": {}, "label": "Orders uploading to ftp", "title": "Uploading Orders"},

           }


@st.cache_data(ttl=60)
def _get_document(col, query, length):
    cursor = db_logs.get_collection(col).find(
        query
    ).sort("createdAt", DESCENDING)

    results = cursor.to_list(length=length)
    return results


def get_last_run(method):
    data = mapping[method]

    res = _get_document(data["col"], data["query"], 1)
    if res is None:
        return "Never", "inverse"

    created_at = res[0]["createdAt"].replace(tzinfo=UTC)
    now = datetime.now(UTC)

    color = "normal"
    if (now - created_at) > data["latest_time"]:
        color = "inverse"

    return humanize.naturaltime(now - created_at), color
