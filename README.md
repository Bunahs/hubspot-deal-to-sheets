# HubSpot to Google Sheets - Deal Synchronization

## 1. Project Overview

This project synchronizes Deal data from HubSpot CRM to Google Sheets using Python.

The application retrieves Deals, associated Contacts, Owners, Pipelines, and Deal Stages from HubSpot, then transforms and synchronizes the data into Google Sheets.

It also generates a Summary worksheet containing Deal statistics.

## 2. Features

- Retrieve Deals from HubSpot CRM.
- Support API pagination when retrieving Deals.
- Retrieve associated Contact information.
- Retrieve Deal Owner information.
- Retrieve Pipeline and Deal Stage names.
- Synchronize Deal data to Google Sheets.
- Prevent duplicate Deals using Deal ID.
- Update existing Deals when the program runs again.
- Insert new Deals into Google Sheets.
- Automatically generate a Summary worksheet.
- Calculate Deal statistics and Conversion Rate.

## 3. Technologies

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| HubSpot CRM API | Retrieve CRM data |
| Google Sheets API | Store and synchronize data |
| Requests | HTTP API requests |
| gspread | Google Sheets integration |
| Google Auth | Service Account authentication |
| python-dotenv | Environment variable management |

## 4. Project Structure

```text
hubspot_deal_to_sheets/
│
├── main.py
├── config.py
├── hubspot.py
├── google_sheets.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
│
└── credentials/
    └── service_account.json
```

### Main Modules

- `main.py`: Main program and workflow orchestration.
- `config.py`: Application configuration and environment variables.
- `hubspot.py`: HubSpot API integration and data retrieval.
- `google_sheets.py`: Google Sheets integration, Deal synchronization, and Summary generation.

## 5. Data Fields

The application synchronizes the following fields:

| Field | Description |
|---|---|
| Deal ID | Unique Deal identifier |
| Deal Name | Deal name |
| Amount | Deal amount |
| Pipeline | Pipeline name |
| Deal Stage | Deal stage name |
| Owner | Assigned Deal Owner |
| Create Date | Deal creation date |
| Close Date | Expected or actual close date |
| Last Modified | Last modification date |
| Associated Contact | Associated Contact information |

## 6. Google Sheets Structure

The application uses two worksheets:

### Deals

Stores synchronized Deal records from HubSpot.

Each Deal is identified by its unique Deal ID.

- Existing Deal: Update the corresponding row.
- New Deal: Insert a new row.

### Summary

Displays Deal statistics:

- Total Deal
- Total Amount
- Won
- Lost
- Conversion Rate
- Deal count by Stage

Conversion Rate is calculated as:

`Won / (Won + Lost)`

## 7. Prerequisites

Before running the application, make sure you have:

- Python 3.10 or later.
- A HubSpot account with API access.
- A HubSpot Private App access token with the required read permissions.
- A Google Cloud Service Account.
- Google Sheets API enabled in Google Cloud.
- A Google Spreadsheet shared with the Service Account email address.

## 8. Installation

### Step 1: Clone the repository

```bash
git clone <repository-url>
cd hubspot_deal_to_sheets
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

## 9. Configuration

### Step 1: Configure environment variables

Create a `.env` file in the project root directory:

```env
HUBSPOT_ACCESS_TOKEN=your_hubspot_access_token
GOOGLE_CREDENTIALS=credentials/service_account.json
GOOGLE_SHEET_ID=your_google_spreadsheet_id
```

Replace the placeholder values with your actual configuration.

### Step 2: Configure Google Service Account

1. Create a Service Account in Google Cloud.
2. Enable Google Sheets API.
3. Download the Service Account JSON key.
4. Place the JSON file inside the `credentials/` directory.
5. Share the target Google Spreadsheet with the Service Account email address as an Editor.

**Security Notice:** Never commit `.env` files, Service Account JSON keys, or API tokens to GitHub.

## 10. Run the Application

Run the following command:

```bash
python main.py
```

The application will:

1. Validate configuration.
2. Retrieve Pipeline and Stage information.
3. Retrieve all Deals from HubSpot.
4. Retrieve associated Contacts and Owners.
5. Transform and prepare Deal records.
6. Connect to Google Sheets.
7. Synchronize Deal records.
8. Update the Summary worksheet.

## 11. Synchronization Logic

The application uses Deal ID as the unique identifier.

| Condition | Action |
|---|---|
| Deal ID already exists | Update existing row |
| Deal ID does not exist | Insert new row |

This approach prevents duplicate Deal records when the synchronization process runs repeatedly.

## 12. Current Test Result

The application has been tested with a sample HubSpot Deal.

Verified operations:

- HubSpot API connection.
- Google Sheets connection.
- Deal retrieval.
- Contact retrieval.
- Owner retrieval.
- Pipeline and Stage mapping.
- Deal synchronization.
- Duplicate prevention on repeated runs.
- Summary worksheet update.

Sample synchronization result:

```text
Total Deals processed: 1
Deals updated: 1
New Deals inserted: 0

Summary updated successfully!

All tasks completed successfully!
```

## 13. Project Purpose

This project was developed as an internship task at Saigon Trade to demonstrate CRM data integration, API communication, data transformation, and Google Sheets automation using Python.