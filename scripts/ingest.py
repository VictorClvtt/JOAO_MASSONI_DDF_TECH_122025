import os
import glob
import pandas as pd
import gspread

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from gspread_dataframe import set_with_dataframe

from scripts.utils.env import write_env_var

# ======================
# Main ingestion function
# ======================
def ingest_data_to_sheets(
    csv_path: str = None,        # caminho de um CSV individual
    csv_folder: str = None,      # caminho de uma pasta com múltiplos CSVs
    secret_path: str = "client_secret.json",
    env_path: str = ".env",
    folder_name: str = "dadosfera",
    spreadsheet_name: str = "raw_orders"
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
    print(f"[INFO] Checking if folder '{folder_name}' exists")

    query = (
        f"name='{folder_name}' and "
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
        print(f"[INFO] Folder '{folder_name}' found (id={folder_id})")
    else:
        print(f"[INFO] Folder '{folder_name}' not found, creating it")

        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }

        folder = drive_service.files().create(
            body=folder_metadata,
            fields="id"
        ).execute()

        folder_id = folder["id"]
        print(f"[INFO] Folder '{folder_name}' created (id={folder_id})")

    # ======================
    # 3️⃣ Create spreadsheet
    # ======================
    print(f"[INFO] Creating spreadsheet '{spreadsheet_name}'")

    spreadsheet = gspread_client.create(
        spreadsheet_name,
        folder_id=folder_id
    )

    worksheet = spreadsheet.sheet1
    spreadsheet_id = spreadsheet.id

    print("[INFO] Spreadsheet created successfully")
    print(f"[INFO] Spreadsheet ID: {spreadsheet_id}")

    # ======================
    # 4️⃣ Share spreadsheet publicly
    # ======================
    print("[INFO] Setting spreadsheet to public (anyone with link can view)")

    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body={
            "type": "anyone",
            "role": "reader"
        }
    ).execute()

    print("[INFO] Spreadsheet shared successfully")

    # ======================
    # 5️⃣ Load CSV(s)
    # ======================
    if csv_folder:
        print(f"[INFO] Reading all CSV files in folder '{csv_folder}'")
        all_files = glob.glob(os.path.join(csv_folder, "*.csv"))
        df_list = [pd.read_csv(f) for f in all_files]
        df = pd.concat(df_list, ignore_index=True)
        print(f"[INFO] {len(all_files)} CSV files loaded and concatenated")
    elif csv_path:
        print(f"[INFO] Reading CSV file from '{csv_path}'")
        df = pd.read_csv(csv_path)
    else:
        raise ValueError("É necessário fornecer 'csv_path' ou 'csv_folder'.")

    # ======================
    # 6️⃣ Upload data to Google Sheets
    # ======================
    print("[INFO] Uploading data to Google Sheets")
    set_with_dataframe(worksheet, df)
    print("[INFO] Data uploaded successfully")

    # ======================
    # 7️⃣ Generate CSV URL and persist to .env
    # ======================
    csv_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/export?format=csv"
    )

    print(f"[INFO] Generated CSV export URL")
    print(f"[INFO] {csv_url}")

    write_env_var("GOOGLE_SHEETS_CSV_URL", csv_url, env_path)
    print("[INFO] GOOGLE_SHEETS_CSV_URL written to .env")


if __name__ == "__main__":
    ingest_data_to_sheets(
        csv_folder="./data/clean/clean_orders",
        secret_path="client_secret.json",
        env_path=".env",
        spreadsheet_name="clean_orders"
    )
