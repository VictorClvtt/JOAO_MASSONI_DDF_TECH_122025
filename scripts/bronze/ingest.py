import os
import pandas as pd
import gspread

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from gspread_dataframe import set_with_dataframe


# ======================
# Utils
# ======================
def write_env_var(key: str, value: str, env_path: str = ".env") -> None:
    lines = []

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()

    with open(env_path, "w") as f:
        found = False
        for line in lines:
            if line.startswith(f"{key}="):
                f.write(f"{key}={value}\n")
                found = True
            else:
                f.write(line)

        if not found:
            f.write(f"{key}={value}\n")


# ======================
# Main ingestion function
# ======================
def ingest_data_to_sheets(
    csv_path: str,
    secret_path: str = "client_secret.json",
    env_path: str = ".env"
) -> None:
    SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    TOKEN_FILE = "token.json"

    # ======================
    # 1️⃣ OAuth Authentication
    # ======================
    print("[INFO] Starting OAuth authentication")

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        print("[INFO] Loaded existing token")
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            secret_path,
            SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

        print("[INFO] New token generated and saved")

    # Initialize clients
    gspread_client = gspread.authorize(creds)
    drive_service = build("drive", "v3", credentials=creds)

    print("[INFO] Google Drive and Sheets clients initialized")

    # ======================
    # 2️⃣ Create or find folder
    # ======================
    FOLDER_NAME = "dadosfera"
    print(f"[INFO] Checking if folder '{FOLDER_NAME}' exists")

    query = (
        f"name='{FOLDER_NAME}' and "
        "mimeType='application/vnd.google-apps.folder' and "
        "trashed=false"
    )

    results = drive_service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    if files:
        folder_id = files[0]["id"]
        print(f"[INFO] Folder '{FOLDER_NAME}' found (id={folder_id})")
    else:
        print(f"[INFO] Folder '{FOLDER_NAME}' not found, creating it")

        folder_metadata = {
            "name": FOLDER_NAME,
            "mimeType": "application/vnd.google-apps.folder"
        }

        folder = drive_service.files().create(
            body=folder_metadata,
            fields="id"
        ).execute()

        folder_id = folder["id"]
        print(f"[INFO] Folder '{FOLDER_NAME}' created (id={folder_id})")

    # ======================
    # 3️⃣ Create spreadsheet
    # ======================
    SPREADSHEET_NAME = "raw_orders"
    print(f"[INFO] Creating spreadsheet '{SPREADSHEET_NAME}'")

    spreadsheet = gspread_client.create(
        SPREADSHEET_NAME,
        folder_id=folder_id
    )

    worksheet = spreadsheet.sheet1
    spreadsheet_id = spreadsheet.id

    print("[INFO] Spreadsheet created successfully")
    print(f"[INFO] Spreadsheet ID: {spreadsheet_id}")

    # ======================
    # 4️⃣ Upload CSV data
    # ======================
    print(f"[INFO] Reading CSV file from '{csv_path}'")

    df = pd.read_csv(csv_path)

    print("[INFO] Uploading data to Google Sheets")
    set_with_dataframe(worksheet, df)

    print("[INFO] Data uploaded successfully")

    # ======================
    # 5️⃣ Generate CSV URL and persist to .env
    # ======================
    csv_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/export?format=csv"
    )

    print(f"[INFO] Generated CSV export URL")
    print(f"[INFO] {csv_url}")

    write_env_var("GOOGLE_SHEETS_CSV_URL", csv_url, env_path)

    print("[INFO] GOOGLE_SHEETS_CSV_URL written to .env")


# ======================
# Entrypoint
# ======================
if __name__ == "__main__":
    ingest_data_to_sheets(
        csv_path="./data/raw/synthetic_data_full.csv",
        secret_path="client_secret.json",
        env_path=".env"
    )
