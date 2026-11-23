
import gspread

from config import (
    GOOGLE_CREDENTIALS,
    GOOGLE_SHEET_ID
)


SHEET_HEADERS = [
    "Deal ID",
    "Deal Name",
    "Amount",
    "Pipeline",
    "Deal Stage",
    "Owner",
    "Create Date",
    "Close Date",
    "Last Modified",
    "Associated Contact"
]


def get_google_sheet():
    """
    Kết nối và lấy worksheet Deals.
    """

    client = gspread.service_account(
        filename=GOOGLE_CREDENTIALS
    )

    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)

    worksheet = spreadsheet.worksheet("Deals")

    return worksheet


def get_summary_sheet():
    """
    Lấy worksheet Summary, nếu chưa có thì tạo mới.
    """

    client = gspread.service_account(
        filename=GOOGLE_CREDENTIALS
    )

    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)

    try:
        worksheet = spreadsheet.worksheet("Summary")

    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title="Summary",
            rows=100,
            cols=10
        )

    return worksheet


def sync_deals_to_sheet(worksheet, rows):
    """
    Đồng bộ Deal lên Google Sheets.
    Deal đã tồn tại thì cập nhật.
    Deal mới thì thêm vào cuối bảng.
    """

    print("\n========== GOOGLE SHEETS SYNC ==========")

    try:
        # 1. Kiểm tra và tạo tiêu đề
        current_headers = worksheet.row_values(1)

        if current_headers != SHEET_HEADERS:
            worksheet.update(
                values=[SHEET_HEADERS],
                range_name="A1:J1"
            )
            print("Sheet headers: UPDATED")

        # 2. Đọc dữ liệu hiện tại
        existing_data = worksheet.get_all_values()

        # Tạo bảng tra cứu Deal ID -> số dòng
        existing_deals = {}

        for row_number, row in enumerate(existing_data[1:], start=2):
            if row and row[0]:
                existing_deals[str(row[0])] = row_number

        # 3. Phân loại Deal cần cập nhật và thêm mới
        rows_to_update = []
        rows_to_insert = []

        for row in rows:
            deal_id = str(row[0])

            if deal_id in existing_deals:
                row_number = existing_deals[deal_id]

                rows_to_update.append({
                    "range": f"A{row_number}:J{row_number}",
                    "values": [row]
                })

            else:
                rows_to_insert.append(row)

        # 4. Cập nhật Deal đã tồn tại
        if rows_to_update:
            worksheet.batch_update(
                rows_to_update,
                value_input_option="USER_ENTERED"
            )

        # 5. Thêm Deal mới
        if rows_to_insert:
            worksheet.append_rows(
                rows_to_insert,
                value_input_option="USER_ENTERED"
            )

        print("Total Deals processed:", len(rows))
        print("Deals updated:", len(rows_to_update))
        print("New Deals inserted:", len(rows_to_insert))

        return True

    except Exception as error:
        print("Google Sheets Sync Error:", repr(error))
        return False


def update_summary_sheet(worksheet, pipelines_map):
    """
    Tạo báo cáo thống kê Deal trên Google Sheets.
    """

    print("\n========== SUMMARY UPDATE ==========")

    try:
        # Lấy danh sách Stage từ HubSpot
        stage_names = []

        for pipeline in pipelines_map.values():
            for stage in pipeline["stages"].values():
                stage_name = stage["name"]

                if stage_name not in stage_names:
                    stage_names.append(stage_name)

        # Tạo nội dung Summary
        summary_data = [
            ["SAIGON TRADE - DEAL SUMMARY", ""],
            ["Metric", "Value"],
            ["Total Deal", "=COUNTA(Deals!A2:A)"],
            ["Total Amount", "=SUM(Deals!C2:C)"],
            ["Won", '=COUNTIF(Deals!E2:E;"Closed Won")'],
            ["Lost", '=COUNTIF(Deals!E2:E;"Closed Lost")'],
            ["Conversion Rate", "=IFERROR(B5/(B5+B6);0)"],
            ["", ""],
            ["Deal Stage", "Total"]
        ]

        # Thêm công thức thống kê từng Stage
        for stage_name in stage_names:
            formula = f'=COUNTIF(Deals!E2:E;"{stage_name}")'

            summary_data.append([
                stage_name,
                formula
            ])

        # Xóa nội dung cũ và ghi dữ liệu mới
        worksheet.clear()

        worksheet.update(
            values=summary_data,
            range_name=f"A1:B{len(summary_data)}",
            value_input_option="USER_ENTERED"
        )

        # Định dạng tỷ lệ phần trăm
        worksheet.format(
            "B7",
            {
                "numberFormat": {
                    "type": "PERCENT",
                    "pattern": "0.00%"
                }
            }
        )

        print("Summary updated successfully!")
        print("Total stages:", len(stage_names))

        return True

    except Exception as error:
        print("Summary Update Error:", repr(error))
        return False


def test_google_connection():
    """Kiểm tra kết nối Google Sheets."""

    print("\n========== GOOGLE SHEETS TEST ==========")

    try:
        # Xác thực Service Account
        client = gspread.service_account(
            filename=GOOGLE_CREDENTIALS
        )

        # Mở Google Sheet bằng ID
        spreadsheet = client.open_by_key(
            GOOGLE_SHEET_ID
        )

        print("Google Sheets connection: SUCCESS")
        print("Spreadsheet title:", spreadsheet.title)

        # Hiển thị danh sách worksheet hiện có
        worksheets = spreadsheet.worksheets()

        print("\nAvailable worksheets:")

        for worksheet in worksheets:
            print(
                f"- {worksheet.title} "
                f"({worksheet.row_count} rows, "
                f"{worksheet.col_count} columns)"
            )

        return True

    except gspread.exceptions.APIError as error:
        print("Google API Error:", error)

    except gspread.exceptions.SpreadsheetNotFound:
        print("Spreadsheet not found.")
        print("Check GOOGLE_SHEET_ID and sharing permissions.")

    except FileNotFoundError as error:
        print("Credentials file error:", error)

    except Exception as error:
        print("Google Sheets connection error:", error)

    return False
