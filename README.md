# Azure Drive

Azure Drive is a project designed to interact with Microsoft Azure's cloud storage solutions, providing a simple interface for managing files, folders, and data in Azure Blob Storage. This repository makes it easier to upload, download, organize, and access files securely from Azure.

## Features

- Upload files to Azure Blob Storage
- Download files from Azure Blob Storage
- List and organize blobs/files in containers
- Secure authentication with Azure credentials
- Easy integration into existing Python projects

## Getting Started

### Prerequisites

- Python 3.7+
- An Azure account with access to Blob Storage
- Azure SDK for Python (`azure-storage-blob`)

### Installation

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Login to Azure:
    ```bash
    az login
    ```

3. Get your subscription ID and add it to the `.env` file.

4. Set up infrastructure:
    ```bash
    cd infrastructure
    python infra.py
    ```

5. Copy the connection string and add it into your `.env` file.

6. Start the app:
    ```bash
    cd ..
    python main.py
    ```

7. Open the app in your browser: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for suggestions and bug fixes.

## License

This project is licensed under the MIT License.

## Contact

For questions or support, open an issue on GitHub or reach out to Rudraksh121a.
