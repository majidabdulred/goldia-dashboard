import streamlit as st

from database import db

st.set_page_config(
    layout="wide",
    page_title="Script Dashboard"
)


def main_page():
    """Defines the content for the Main page."""
    st.title("Script Run Dashboard")
    st.header("Main Scripts")

    responses = {}
    for action, values in list(db.mapping.items()):
        age, color = db.get_last_run(action)
        responses[action] = {"label": values["label"], "value": values["title"], "delta": age, "delta_color": color,
                             "border": True}

    main_tasks = st.columns(2)

    main_tasks[0].metric(**responses["UPDATE_TRACKING_NUMBER_SHIPSTATION"])
    main_tasks[1].metric(**responses["UPDATE_TRACKING_NUMBER_WALMART"])

    main_tasks2 = st.columns(2)
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


def about_page():
    """Defines the content for the About page."""
    st.title("About This Dashboard")


# --- Navigation Setup ---

# Define the pages in your app
# We are changing this from a dictionary to a list of st.Page objects
# This is a more robust way to pass pages to st.navigation
pages = [
    st.Page(main_page, title="Main", default=True),
    st.Page(about_page, title="About"),
]

# Create the navigation UI in the sidebar
pg = st.navigation(pages, position="sidebar")

# --- Run the App ---
# This will automatically run the function associated with the page
# the user selects from the sidebar.
pg.run()
