import streamlit as st
from database import db
from concurrent.futures import wait
from async_runner import async_runner  # the

st.set_page_config(
    layout="wide",
    page_title="Script Dashboard"
)


def get_responses(coros):
    futures = [async_runner.submit(coro) for coro in coros]
    done, not_done = wait(futures, timeout=10)
    results = [r.result() for r in done]
    for fut in not_done:
        try:
            fut.cancel()
        except Exception:
            pass
    return results


def main_page():
    """Defines the content for the Main page."""
    st.title("Script Run Dashboard")
    st.header("Main Scripts")

    coros = [db.get_last_run(action) for action in db.mapping]
    results = get_responses(coros)

    responses = {r[0]: {"label": db.mapping[r[0]]["label"], "value": db.mapping[r[0]]["title"], "delta": r[1],
                        "delta_color": r[2],
                        "border": True} for r in results}



    main_tasks = st.columns(3)

    main_tasks[0].metric(**responses["UPDATE_TRACKING_NUMBER_SHIPSTATION"])
    main_tasks[1].metric(**responses["UPDATE_TRACKING_NUMBER_WALMART"])

    main_tasks2 = st.columns(3)
    main_tasks2[0].metric(**responses["ORDER_TAGGING"])
    main_tasks2[1].metric(**responses["UPLOAD_ORDERS"])

    st.header("Price/Quantity update scripts")

    amazon_prices_inventory = st.columns(3)
    amazon_prices_inventory[0].metric(**responses["PRICE_UPDATE_AMAZON_US"])
    amazon_prices_inventory[1].metric(**responses["PRICE_UPDATE_AMAZON_AU"])


    shopify_prices = st.columns(4)
    shopify_prices[0].metric(**responses["PRICE_UPDATE_SHOPIFY_US"])
    shopify_prices[1].metric(**responses["PRICE_UPDATE_SHOPIFY_AU"])
    shopify_prices[2].metric(**responses["PRICE_UPDATE_SHOPIFY_CA"])
    shopify_prices[3].metric(**responses["PRICE_UPDATE_SHOPIFY_UK"])


    shopify_quantity = st.columns(4)
    shopify_quantity[0].metric(**responses["INVENTORY_UPDATE_SHOPIFY_US"])
    shopify_quantity[1].metric(**responses["INVENTORY_UPDATE_SHOPIFY_AU"])
    shopify_quantity[2].metric(**responses["INVENTORY_UPDATE_SHOPIFY_CA"])
    shopify_quantity[3].metric(**responses["INVENTORY_UPDATE_SHOPIFY_UK"])

    st.header("Downloading Scripts")

    shopify_downloads = st.columns(4)
    shopify_downloads[0].metric(**responses["DOWNLOAD_SHOPIFY_US"])
    shopify_downloads[1].metric(**responses["DOWNLOAD_SHOPIFY_AU"])
    shopify_downloads[2].metric(**responses["DOWNLOAD_SHOPIFY_UK"])
    shopify_downloads[3].metric(**responses["DOWNLOAD_SHOPIFY_CA"])


    amazon_downloads = st.columns(4)
    amazon_downloads[0].metric(**responses["DOWNLOAD_AMAZON_US"])
    amazon_downloads[1].metric(**responses["DOWNLOAD_AMAZON_AU"])
    amazon_downloads[2].metric(**responses["DOWNLOAD_MASTERFILE"])


def get_tracking_updated_orders():
    """Defines the content for the About page."""
    st.title("Tracking Number Updated")
    responses = get_responses([db.get_tracking_updated_orders()])

    df =responses[0]

    st.dataframe(df,height=700)

def get_uploaded_orders():
    """Defines the content for the About page."""
    st.title("Tracking Number Updated")
    responses = get_responses([db.get_uploaded_orders()])

    df =responses[0]

    st.dataframe(df,height=700)


def shopify_updates():
    """Defines the content for the About page."""
    st.title("Tracking Number Updated")
    responses = get_responses([db.shopify_updates()])

    df =responses[0]

    st.dataframe(df,height=700)


# --- Navigation Setup ---

# Define the pages in your app
# We are changing this from a dictionary to a list of st.Page objects
# This is a more robust way to pass pages to st.navigation
pages = [
    st.Page(main_page, title="Main", default=True),
    st.Page(get_tracking_updated_orders, title="Tracking Updated"),
    st.Page(get_uploaded_orders, title="Uploaded Orders"),
    st.Page(shopify_updates, title="Shopify Updates"),
]

# Create the navigation UI in the sidebar
pg = st.navigation(pages, position="sidebar")

# --- Run the App ---
# This will automatically run the function associated with the page
# the user selects from the sidebar.
pg.run()
