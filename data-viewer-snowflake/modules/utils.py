import os, configparser
from sys import platform
import pandas as pd
from snowflake.snowpark import Session
import streamlit as st

def isLocal():
    return platform == "win32";

def getFullPath(filename):
    crtdir = os.path.dirname(__file__)
    pardir = os.path.abspath(os.path.join(crtdir, os.pardir))
    return f"{pardir}/{filename}"

@st.cache_data(show_spinner="Running a Snowflake query...")
def getDataFrame(session, query):
    rows = session.sql(query).collect()
    return pd.DataFrame(rows).convert_dtypes()

@st.cache_resource(show_spinner="Connecting to Snowflake...", max_entries=10)
def getSession(account, user, password):
    try:
        return Session.builder.configs({
            "account": account,
            "user": user,
            "password": password
        }).create()
    except:
        return None

# customize with your own Snowflake connection parameters
def getLocalSession():
    parser = configparser.ConfigParser()
    parser.read(os.path.join(os.path.expanduser('~'), ".snowsql/config"))
    section = "connections.demo_conn"
    return getSession(parser.get(section, "accountname"),
        parser.get(section, "username"),
        os.environ['SNOWSQL_PWD'])

def getRemoteSession():
    session = None
    with st.form("my-form"):
        account = st.text_input("Account #:")
        user = st.text_input("User Name:")
        password = st.text_input("Password", type='password')
        st.form_submit_button("Connect to Snowflake")
        if len(account) > 0 and len(user) > 0 and len(password) > 0:
            session = getSession(account, user, password)
            if session is None:
                st.error("Cannot connect!")
        if session is not None:
            st.info("Connected to Snowflake.")
    return session
