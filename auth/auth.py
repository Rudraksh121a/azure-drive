from flask import redirect, request, session, url_for
from msal import ConfidentialClientApplication
import os
from dotenv import load_dotenv

load_dotenv()  # Load env variables

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTHORITY = os.getenv("AUTHORITY")
REDIRECT_URI = "http://localhost:5000/getAToken"
SCOPE = ["User.Read"]

msal_app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

all_logged_in_users = []

def login():
    auth_url = msal_app.get_authorization_request_url(
        scopes=SCOPE, redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)

def authorized():
    code = request.args.get("code")
    if not code:
        return "No code returned from Microsoft login."

    result = msal_app.acquire_token_by_authorization_code(
        code, scopes=SCOPE, redirect_uri=REDIRECT_URI
    )

    if "id_token_claims" in result:
        session["user"] = result["id_token_claims"]

        if result["id_token_claims"] not in all_logged_in_users:
            all_logged_in_users.append(result["id_token_claims"])

        return redirect(url_for("home"))
    
    return "Login failed: " + str(result)

def logout():
    session.clear()
    ms_logout = "https://login.microsoftonline.com/common/oauth2/v2.0/logout"
    post_logout_redirect = url_for("home", _external=True)
    return redirect(f"{ms_logout}?post_logout_redirect_uri={post_logout_redirect}")
