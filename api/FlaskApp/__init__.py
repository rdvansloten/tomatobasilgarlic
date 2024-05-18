import os
from flask import Flask, redirect, request, session, jsonify, Response
import logging
from datetime import datetime, timezone, timedelta, time as dtime
import sys
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


# Environment variables
managed_identity_client_id = os.environ["MANAGED_IDENTITY_CLIENT_ID"]
key_vault_name = os.environ["KEY_VAULT_NAME"]
home_url = f"yourdomain." + os.environ["HOME_URL"]

# Authentication
managed_identity_credential = DefaultAzureCredential(managed_identity_client_id=managed_identity_client_id, exclude_interactive_browser_credential=False, additionally_allowed_tenants="*")

# Retrieve Key Vault Secrets
key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
key_vault_client = SecretClient(vault_url=key_vault_uri, credential=managed_identity_credential)

# Logging Settings
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename='function.log', encoding='utf-8', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# Start app
app = Flask(__name__)
app.config["SECRET_KEY"] = key_vault_client.get_secret("flask-secret-key").value
app.config['SESSION_COOKIE_DOMAIN'] = f".{home_url}"
app.config["SESSION_COOKIE_NAME"] = "your-session"
app.config["REMEMBER_COOKIE_DOMAIN"] = "None"

@app.route("/")
def home():
    return "Not allowed."

@app.route("/status")
def status():
    try:
        session["access_token"]
        logging.info("Access token found")
        result = {
        "rc": "loggedin",
        "msg": f"User is logged in with access token {session['access_token']}."
        }
    except:
        logging.info("No access token found")
        result = {
        "rc": "notloggedin",
        "msg": f"User is not logged in."
        }
        
    return jsonify(result)
