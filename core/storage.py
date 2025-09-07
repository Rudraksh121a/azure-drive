from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import logging



# Load environment variables from .env
load_dotenv()

# Use correct env variable name
CONNECTION_STRING = os.getenv("connecting_string")
if not CONNECTION_STRING:
    raise ValueError("Missing 'connecting_string' in .env file!")

# Global BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)


def container_exists(container_name: str) -> bool:
    """Check if a container exists."""
    try:
        container_client = blob_service_client.get_container_client(container_name)
        return container_client.exists()
    except Exception as e:
        print(f"Error checking container: {e}")
        return False


def container_creator(container_name: str) -> str:
    """Create a new container."""
    try:
        blob_service_client.create_container(container_name)
        return f"Container '{container_name}' created successfully."
    except Exception as e:
        return f"Error creating container: {str(e)}"


def create_virtual_folder(container_name: str, folder_name: str) -> str:
    """Create a virtual folder (placeholder blob with .keep)."""
    try:
        if not folder_name.endswith("/"):
            folder_name += "/"

        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(folder_name + ".keep")
        blob_client.upload_blob(b"", overwrite=True)

        return "Folder created."
    except Exception as e:
        return f"Error creating folder: {str(e)}"


def list_virtual_folders(container_name: str) -> list[str]:
    """List all virtual folders (blobs ending with .keep)."""
    try:
        container_client = blob_service_client.get_container_client(container_name)
        folders = [
            blob.name.replace(".keep", "")
            for blob in container_client.list_blobs()
            if blob.name.endswith(".keep")
        ]
        return folders
    except Exception as e:
        print(f"Error listing folders: {e}")
        return []


def upload_file_to_folder(container_name: str, folder_name: str, file_stream, file_name: str) -> str:
    """Upload a file into a virtual folder inside a container."""
    try:
        if folder_name and not folder_name.endswith("/"):
            folder_name += "/"

        blob_path = f"{folder_name}{file_name}"
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)
        blob_client.upload_blob(file_stream, overwrite=True)

        return f"File uploaded"
    except Exception as e:
        return f"Error uploading file: {str(e)}"


def list_files_in_folder(container_name: str, folder_name: str) -> list[dict]:
    """
    List files inside a virtual folder (excluding .keep) and generate temporary access URLs.
    Returns a list of dicts: [{'name': filename, 'url': file_url}, ...]
    """
    try:
        container_client = blob_service_client.get_container_client(container_name)
        if folder_name and not folder_name.endswith("/"):
            folder_name += "/"

        files = []
        for blob in container_client.list_blobs(name_starts_with=folder_name):
            if not blob.name.endswith(".keep"):
                file_name = blob.name[len(folder_name):]
                file_url = get_file_url(container_name, folder_name, file_name)
                files.append({"name": file_name, "url": file_url})

        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def get_file_url(container_name: str, folder_name: str, file_name: str, expiry_minutes: int = 60) -> str:
    """Generate a temporary URL to access a file in Azure Blob Storage."""
    if folder_name and not folder_name.endswith("/"):
        folder_name += "/"

    blob_client = blob_service_client.get_blob_client(container_name, folder_name + file_name)

    # Ensure account key exists
    if not hasattr(blob_service_client.credential, "account_key"):
        raise ValueError("Missing account key in connection string for SAS generation!")

    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=folder_name + file_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(minutes=expiry_minutes)
    )

    return f"{blob_client.url}?{sas_token}"

def delete_item(container_name: str, folder_name: str = None, file_name: str = None) -> str:
    """
    Delete a specific file or a virtual folder from Azure Blob Storage.
    
    - If file_name is provided, it deletes that specific file inside the folder.
    - If only folder_name is provided, it deletes the entire folder and all its contents.
    """
    try:
        container_client = blob_service_client.get_container_client(container_name)

        # Delete a specific file
        if file_name:
            if folder_name and not folder_name.endswith("/"):
                folder_name += "/"
            blob_path = f"{folder_name or ''}{file_name}"
            blob_client = container_client.get_blob_client(blob_path)
            blob_client.delete_blob()
            return f"File '{file_name}' deleted from folder '{folder_name or ''}'."

        # Delete an entire folder
        elif folder_name:
            if not folder_name.endswith("/"):
                folder_name += "/"
            blobs_to_delete = [blob.name for blob in container_client.list_blobs(name_starts_with=folder_name)]
            if not blobs_to_delete:
                return f"No items found in folder '{folder_name}' to delete."
            for blob_name in blobs_to_delete:
                blob_client = container_client.get_blob_client(blob_name)
                blob_client.delete_blob()
            return f" Folder '{folder_name}' and all its contents have been deleted."

        else:
            return "Error: Must provide either folder_name or file_name to delete."

    except Exception as e:
        return f"Error deleting item: {str(e)}"

