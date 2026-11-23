import requests

from config import validate_config

from hubspot import (
    get_all_deals,
    get_contacts_by_ids,
    get_all_owners,
    get_deal_pipelines
)

from google_sheets import (
    get_google_sheet,
    get_summary_sheet,
    sync_deals_to_sheet,
    update_summary_sheet
)

def prepare_deal_rows(deals, contacts_map, owners_map, pipelines_map):
    rows = []

    for deal in deals:
        properties = deal.get("properties", {})

        deal_id = deal.get("id")
        owner_id = properties.get("hubspot_owner_id")

        # Lấy thông tin Owner
        owner = owners_map.get(str(owner_id)) if owner_id else None
        owner_name = owner["name"] if owner else "Chưa phân công"

        # Lấy tên Pipeline và Stage
        pipeline_id = properties.get("pipeline")
        stage_id = properties.get("dealstage")

        pipeline_info = pipelines_map.get(pipeline_id, {})
        pipeline_name = pipeline_info.get("name", pipeline_id)

        stage_info = pipeline_info.get("stages", {}).get(stage_id, {})
        stage_name = stage_info.get("name", stage_id)

        # Lấy thông tin Contact
        associated_contacts = (
            deal.get("associations", {})
            .get("contacts", {})
            .get("results", [])
        )

        contact_names = []

        for contact in associated_contacts:
            contact_id = str(contact.get("id"))
            contact_info = contacts_map.get(contact_id)

            if contact_info:
                contact_name = contact_info.get("name")
                contact_email = contact_info.get("email")

                if contact_name and contact_email:
                    contact_names.append(
                        f"{contact_name} ({contact_email})"
                    )
                elif contact_name:
                    contact_names.append(contact_name)

        associated_contact = ", ".join(contact_names)

        row = [
            deal_id,
            properties.get("dealname"),
            properties.get("amount"),
            pipeline_name,
            stage_name,
            owner_name,
            properties.get("createdate"),
            properties.get("closedate"),
            properties.get("hs_lastmodifieddate"),
            associated_contact
        ]

        rows.append(row)

    return rows

def main():
    """Chương trình chính."""

    print("===================================")
    print("SAIGON TRADE - DEAL SYNC")
    print("HUBSPOT TO GOOGLE SHEETS")
    print("===================================")

    # 1. Kiểm tra cấu hình
    try:
        validate_config()
        print("Configuration: VALID")

    except (ValueError, FileNotFoundError) as error:
        print("Configuration Error:", error)
        return

    # 2. Lấy thông tin Pipeline và Stage
    print("\n========== HUBSPOT PIPELINE DATA ==========")

    try:
        pipelines_map = get_deal_pipelines()

        if not pipelines_map:
            print("No Pipeline data found.")
            return

        for pipeline_id, pipeline in pipelines_map.items():
            print("\nPipeline:", pipeline["name"])
            print("Pipeline ID:", pipeline_id)

            for stage_id, stage in pipeline["stages"].items():
                print(
                    "Stage:", stage["name"],
                    "| ID:", stage_id,
                    "| Closed:", stage["is_closed"],
                    "| Won:", stage["is_won"]
                )

    except requests.exceptions.RequestException as error:
        print("Pipeline API Error:", error)
        return

    # 3. Lấy toàn bộ Deal
    deals = get_all_deals()

    if deals is None:
        print("Cannot retrieve Deals.")
        return

    # 4. Thu thập Contact ID duy nhất
    contact_ids = set()

    for deal in deals:
        contacts = (
            deal.get("associations", {})
            .get("contacts", {})
            .get("results", [])
        )

        for contact in contacts:
            contact_ids.add(str(contact.get("id")))

    contact_ids = list(contact_ids)

    print("\nTotal unique Contact IDs:", len(contact_ids))

    # 5. Lấy thông tin Contact
    contacts_map = get_contacts_by_ids(contact_ids)

    if contacts_map is None:
        print("Cannot retrieve Contact details.")
        return

    print("Contacts retrieved:", len(contacts_map))

    # 6. Lấy thông tin Owner
    owners_map = get_all_owners()

    if owners_map is None:
        print("Cannot retrieve Owner details.")
        return

    print("Owners retrieved:", len(owners_map))

    # 7. Chuẩn bị dữ liệu đồng bộ
    deal_rows = prepare_deal_rows(
        deals,
        contacts_map,
        owners_map,
        pipelines_map
    )

    # 8. Hiển thị dữ liệu sau khi kết hợp
    print("\n========== ENRICHED DEAL PREVIEW ==========")

    for row in deal_rows[:5]:
        print("\n------------------------------")
        print("Deal ID:", row[0])
        print("Deal Name:", row[1])
        print("Amount:", row[2])
        print("Pipeline:", row[3])
        print("Deal Stage:", row[4])
        print("Owner:", row[5])
        print("Created Date:", row[6])
        print("Close Date:", row[7])
        print("Last Modified:", row[8])
        print("Associated Contacts:", row[9] or "Không có")

    # 9. Kết nối Google Sheets
    try:
        worksheet = get_google_sheet()
        print("\nGoogle Sheets connection: SUCCESS")

    except Exception as error:
        print("Cannot open Deals worksheet:", error)
        return

    # 10. Đồng bộ Deal
    sync_success = sync_deals_to_sheet(
        worksheet,
        deal_rows
    )

    if not sync_success:
        print("Deal synchronization failed.")
        return

    # 11. Cập nhật Summary
    try:
        summary_worksheet = get_summary_sheet()

        summary_success = update_summary_sheet(
            summary_worksheet,
            pipelines_map
        )

    except Exception as error:
        print("Cannot update Summary:", error)
        return

    if not summary_success:
        print("Summary update failed.")
        return

    # 12. Kết quả cuối cùng
    print("\n========== FINAL RESULT ==========")
    print("Configuration: SUCCESS")
    print("HubSpot: SUCCESS")
    print("Deal retrieval: SUCCESS")
    print("Contact retrieval: SUCCESS")
    print("Owner retrieval: SUCCESS")
    print("Pipeline retrieval: SUCCESS")
    print("Google Sheets: SUCCESS")
    print("Deal synchronization: SUCCESS")
    print("Summary update: SUCCESS")
    print("\nAll tasks completed successfully!")

if __name__ == "__main__":
    main()





