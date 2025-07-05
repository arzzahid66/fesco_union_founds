from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
import numpy as np
import os
import json
from dotenv import load_dotenv
load_dotenv()

SPREADSHEET_ID = '14BiC6WpAd0UyWae6Efg1AQTwnCWpDTR9dla7FbhzHB8'

def get_sheets_service():
    """Get Google Sheets service with credentials from environment variables"""
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        
        # Option 1: If you store the entire JSON as a string in environment variable
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if credentials_json:
            # Parse the JSON string
            credentials_info = json.loads(credentials_json)
            creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
        else:
            # Option 2: If you store individual components in separate environment variables
            credentials_info = {
                "type": "service_account",
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),  # Handle newlines
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
                "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
                "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
                "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN')
            }
            creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
        
        service = build('sheets', 'v4', credentials=creds)
        return service.spreadsheets()
    except Exception as e:
        print(f"Error creating Google Sheets service: {str(e)}")
        raise e

def check_sheet_exists(sheet_name):
    """Check if a sheet exists in the spreadsheet"""
    try:
        service = get_sheets_service()
        spreadsheet = service.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        return sheet_name in sheet_names
    except Exception as e:
        print(f"Error checking if sheet exists: {str(e)}")
        return False

def clean_data_for_sheets(data):
    """Clean data to ensure it's compatible with Google Sheets API"""
    if isinstance(data, pd.DataFrame):
        # Replace NaN, None, and inf values with empty strings
        data = data.replace([np.nan, np.inf, -np.inf], '')
        # Convert all data to strings to avoid type issues
        data = data.astype(str)
        return data.values.tolist()
    elif isinstance(data, list):
        cleaned_data = []
        for row in data:
            cleaned_row = []
            for cell in row:
                if pd.isna(cell) or cell is None or cell == 'nan' or str(cell).lower() == 'nan':
                    cleaned_row.append('')
                else:
                    cleaned_row.append(str(cell))
            cleaned_data.append(cleaned_row)
        return cleaned_data
    return data

def read_sheet_data(sheet_name):
    """Read data from Google Sheets with improved error handling and data cleaning"""
    try:
        service = get_sheets_service()
        
        # Read from A1 to ensure we get all data starting from column A
        result = service.values().get(
            spreadsheetId=SPREADSHEET_ID, 
            range=f'{sheet_name}!A:Z'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print(f"No data found in sheet: {sheet_name}")
            return pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])
        
        # Handle case where there might be uneven rows
        max_cols = max(len(row) for row in values) if values else 4
        max_cols = max(max_cols, 4)  # Ensure at least 4 columns
        
        padded_values = []
        for row in values:
            # Pad row to have consistent number of columns
            padded_row = row + [''] * (max_cols - len(row))
            padded_values.append(padded_row)
        
        if len(padded_values) > 1:
            # Use first row as headers
            headers = padded_values[0]
            data_rows = padded_values[1:]
            
            # Ensure we have the correct headers
            if len(headers) >= 4:
                # Take only the first 4 columns if there are more
                headers = headers[:4]
                data_rows = [row[:4] for row in data_rows]
            
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=['Sr', 'Date', 'Name', 'Amount'])
            
            # Clean the dataframe - remove completely empty rows
            df = df.replace('', pd.NA)
            df = df.dropna(how='all')
            df = df.fillna('')
            
            # Filter out rows where all important fields are empty
            df = df[~((df['Date'] == '') & (df['Name'] == '') & (df['Amount'] == ''))]
            
            print(f"Successfully loaded {len(df)} rows from {sheet_name}")
            return df
        else:
            print(f"Only headers found in sheet: {sheet_name}")
            return pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])
            
    except Exception as e:
        print(f"Error reading sheet data from {sheet_name}: {str(e)}")
        return pd.DataFrame(columns=['Sr', 'Date', 'Name', 'Amount'])

def write_sheet_data(sheet_name, data):
    try:
        service = get_sheets_service()
        
        # Clean and prepare data
        if isinstance(data, pd.DataFrame):
            values = clean_data_for_sheets(data)
        elif isinstance(data, list):
            values = clean_data_for_sheets(data)
        else:
            values = data
        
        # Clear the sheet first to start fresh
        clear_request = service.values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{sheet_name}!A:Z'  # Clear all columns starting from A
        ).execute()
        
        # Write new data starting from A1
        body = {'values': values}
        result = service.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{sheet_name}!A1',  # Explicitly start from A1
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return result
    except Exception as e:
        print(f"Error writing sheet data: {str(e)}")
        raise e

def append_sheet_data(sheet_name, data):
    try:
        service = get_sheets_service()
        
        # Clean and prepare data
        if isinstance(data, pd.DataFrame):
            values = clean_data_for_sheets(data)
        else:
            values = clean_data_for_sheets(data)
        
        body = {'values': values}
        result = service.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return result
    except Exception as e:
        print(f"Error appending sheet data: {str(e)}")
        raise e

def create_sheet_if_not_exists(sheet_name):
    """Create a new sheet if it doesn't exist"""
    try:
        service = get_sheets_service()
        
        # Get existing sheets
        spreadsheet = service.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        
        if sheet_name not in sheet_names:
            # Create new sheet
            request = {
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }
            
            batch_update_request = {'requests': [request]}
            service.batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=batch_update_request
            ).execute()
            
            print(f"Created new sheet: {sheet_name}")
        
        return True
    except Exception as e:
        print(f"Error creating sheet: {str(e)}")
        return False