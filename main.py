from flask import Flask, redirect, request, session, url_for, render_template
from auth.auth import login, authorized, logout
import os
from dotenv import load_dotenv
from core.storage import (
    container_exists,
    container_creator,
    create_virtual_folder,
    list_virtual_folders,
    upload_file_to_folder,
    list_files_in_folder
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)


def get_user_container():
    """Return sanitized container name for logged-in user."""
    user = session.get("user")
    if not user:
        return None
    raw_name = user.get("preferred_username", "defaultuser")
    return raw_name.replace("@", "-").replace(".", "-").lower()


@app.route('/')
def home():
    """Home page: list user's folders."""
    user = session.get("user")
    if not user:
        return redirect(url_for("login_route"))

    container_name = get_user_container()
    if not container_exists(container_name):
        container_creator(container_name)

    folders = list_virtual_folders(container_name)
    

    return render_template("home/home.html", user=user, folders=folders)


@app.route('/folder/<path:folder_name>')
def view_folder(folder_name):
    """View files inside a folder."""
    user = session.get("user")
    if not user:
        return redirect(url_for("login_route"))

    container_name = get_user_container()
    files = list_files_in_folder(container_name, folder_name)
    return render_template(
        "home/folder_view.html",
        user=user,
        folder_name=folder_name,
        files=files
    )


@app.route('/upload/<path:folder_name>', methods=['GET', 'POST'])
def upload_file(folder_name):
    """Upload file to a specific folder."""
    user = session.get("user")
    if not user:
        return redirect(url_for("login_route"))

    container_name = get_user_container()

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file:
            result = upload_file_to_folder(
                container_name,
                folder_name,
                uploaded_file.stream,
                uploaded_file.filename
            )
            files = list_files_in_folder(container_name, folder_name)
            return render_template(
                "home/folder_view.html",
                user=user,
                folder_name=folder_name,
                files=files,
                success=result
            )

    return render_template("forms/upload.html", folder_name=folder_name)


@app.route('/create-folder', methods=['GET', 'POST'])
def create_folder():
    """Create a new virtual folder."""
    user = session.get("user")
    if not user:
        return redirect(url_for("login_route"))

    container_name = get_user_container()

    if request.method == "POST":
        folder_name = request.form.get("folder_name")
        if folder_name:
            result = create_virtual_folder(container_name, folder_name)
            folders = list_virtual_folders(container_name)
            return render_template(
                "home/home.html",
                user=user,
                folders=folders,
                success=result
            )

    return render_template("forms/create_folder.html")


@app.route('/login')
def login_route():
    return login()


@app.route('/getAToken')
def authorized_route():
    return authorized()


@app.route('/logout')
def logout_route():
    return logout()


if __name__ == "__main__":
    app.run(debug=True)
