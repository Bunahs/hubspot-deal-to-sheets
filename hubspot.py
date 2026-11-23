
import requests

from config import (
    HUBSPOT_ACCESS_TOKEN,
    HUBSPOT_BASE_URL
)


# Các trường Deal cần lấy theo Task 3
DEAL_PROPERTIES = [
    "dealname",
    "amount",
    "pipeline",
    "dealstage",
    "hubspot_owner_id",
    "createdate",
    "closedate",
    "hs_lastmodifieddate"
]

CONTACT_PROPERTIES = [
    "firstname",
    "lastname",
    "email",
    "phone"
]


def get_all_deals():
    """Lấy toàn bộ Deal từ HubSpot, hỗ trợ phân trang."""

    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/deals"

    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    params = {
        "limit": 100,
        "properties": DEAL_PROPERTIES,
        "associations": "contacts"
    }

    all_deals = []

    print("\n========== FETCH ALL DEALS ==========")

    try:
        while True:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            deals = data.get("results", [])
            all_deals.extend(deals)

            print(f"Retrieved: {len(deals)} deals")
            print(f"Total so far: {len(all_deals)}")

            next_page = data.get("paging", {}).get("next")

            if not next_page:
                break

            params["after"] = next_page["after"]

        print("\nTotal deals retrieved:", len(all_deals))
        return all_deals

    except requests.exceptions.HTTPError as error:
        print("HubSpot API HTTP Error:", error.response.status_code)
        print("Details:", error.response.text[:1000])

    except requests.exceptions.RequestException as error:
        print("HubSpot connection error:", error)

    except (ValueError, KeyError) as error:
        print("Data processing error:", error)

    return None


def get_contacts_by_ids(contact_ids):
    """Lấy thông tin nhiều Contact bằng Batch Read API."""

    if not contact_ids:
        return {}

    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/batch/read"

    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    contacts_map = {}

    for start in range(0, len(contact_ids), 100):
        batch_ids = contact_ids[start:start + 100]

        payload = {
            "inputs": [
                {"id": contact_id}
                for contact_id in batch_ids
            ],
            "properties": CONTACT_PROPERTIES
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            for contact in data.get("results", []):
                contact_id = contact.get("id")
                properties = contact.get("properties", {})

                first_name = properties.get("firstname") or ""
                last_name = properties.get("lastname") or ""

                full_name = f"{first_name} {last_name}".strip()

                contacts_map[contact_id] = {
                    "id": contact_id,
                    "name": full_name,
                    "email": properties.get("email"),
                    "phone": properties.get("phone")
                }

        except requests.exceptions.RequestException as error:
            print("Contact API Error:", error)

            if error.response is not None:
                print("Details:", error.response.text[:1000])

            return None

    return contacts_map


def get_all_owners():
    """Lấy danh sách Owner từ HubSpot."""

    url = f"{HUBSPOT_BASE_URL}/crm/v3/owners"

    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    params = {"limit": 100}
    owners_map = {}

    try:
        while True:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            for owner in data.get("results", []):
                owner_id = str(owner.get("id"))

                first_name = owner.get("firstName") or ""
                last_name = owner.get("lastName") or ""

                owners_map[owner_id] = {
                    "id": owner_id,
                    "name": f"{first_name} {last_name}".strip(),
                    "email": owner.get("email")
                }

            next_page = data.get("paging", {}).get("next")

            if not next_page:
                break

            params["after"] = next_page["after"]

        return owners_map

    except requests.exceptions.RequestException as error:
        print("Owner API Error:", error)

        if error.response is not None:
            print("Details:", error.response.text[:1000])

        return None


def get_deal_pipelines():
    """Lấy danh sách Pipeline và Stage từ HubSpot."""

    url = f"{HUBSPOT_BASE_URL}/crm/v3/pipelines/deals"

    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    pipelines_map = {}

    for pipeline in data.get("results", []):
        pipeline_id = pipeline.get("id")

        stages = {}

        for stage in pipeline.get("stages", []):
            stage_id = stage.get("id")
            metadata = stage.get("metadata", {})

            stages[stage_id] = {
                "name": stage.get("label"),
                "is_closed": metadata.get("isClosed"),
                "is_won": metadata.get("isWon")
            }

        pipelines_map[pipeline_id] = {
            "name": pipeline.get("label"),
            "stages": stages
        }

    return pipelines_map


def test_hubspot_connection():
    """Kiểm tra kết nối HubSpot và lấy thử Deal."""

    print("\n========== HUBSPOT TEST ==========")

    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/deals"

    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    params = {
        "limit": 5,
        "properties": DEAL_PROPERTIES,
        "associations": "contacts"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        deals = data.get("results", [])

        print("HubSpot connection: SUCCESS")
        print(f"Number of deals retrieved: {len(deals)}")

        for deal in deals:
            properties = deal.get("properties", {})

            print("\n------------------------------")
            print("Deal ID:", deal.get("id"))
            print("Deal Name:", properties.get("dealname"))
            print("Amount:", properties.get("amount"))
            print("Pipeline:", properties.get("pipeline"))
            print("Deal Stage:", properties.get("dealstage"))
            print("Owner ID:", properties.get("hubspot_owner_id"))

            contacts = (
                deal.get("associations", {})
                .get("contacts", {})
                .get("results", [])
            )

            print("Associated Contacts:", len(contacts))

        next_page = data.get("paging", {}).get("next")

        if next_page:
            print("\nPagination: Available")
        else:
            print("\nPagination: No next page returned")

        return True

    except requests.exceptions.HTTPError as error:
        print("HubSpot API HTTP Error:", error.response.status_code)
        print("Details:", error.response.text[:1000])

    except requests.exceptions.RequestException as error:
        print("HubSpot connection error:", error)

    except ValueError as error:
        print("HubSpot response error:", error)

    return False
