import streamlit as st
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

load_dotenv()


@st.cache_resource
def get_database():
    DB_SRV = st.secrets["DB_SRV"]
    client: MongoClient = AsyncIOMotorClient(DB_SRV)
    db_logs = client.get_database("scripts_logs")
    return db_logs
