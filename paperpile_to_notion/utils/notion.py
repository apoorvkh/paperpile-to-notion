import requests


NOTION_API_BASE_URL = "https://api.notion.com/v1"
CHAR_LIMIT=2000


def get_headers(notion_token):
    return {
        "Accept": "application/json",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {notion_token}",
    }


def query_db(db_id, headers=None):
    url = f"{NOTION_API_BASE_URL}/databases/{db_id}/query"
    payload = {"page_size": 100}
    response = {"has_more": True}

    pages = []

    while response["has_more"]:
        response = requests.post(url, json=payload, headers=headers, timeout=60).json()
        pages += response["results"]
        payload["start_cursor"] = response["next_cursor"]

    pages = [p for p in pages if p['archived'] is False]

    return pages


def update_page(db_id, properties, update_page_id=None, headers=None):
    payload = {
        "parent": {
            "database_id": db_id,
        },
        "properties": properties,
    }

    if update_page_id is not None:
        url = f"{NOTION_API_BASE_URL}/pages/{update_page_id}"
        response = requests.patch(url, json=payload, headers=headers, timeout=60)
    else:
        url = f"{NOTION_API_BASE_URL}/pages"
        response = requests.post(url, json=payload, headers=headers, timeout=60)

    return response.ok, response.text


def archive_page(page_id, headers=None):
    payload = {
        "archived": True
    }
    url = f"{NOTION_API_BASE_URL}/pages/{page_id}"
    response = requests.patch(url, json=payload, headers=headers, timeout=60)
    return response.ok, response.text


def is_blank_page(page_id, headers=None):
    url = f"{NOTION_API_BASE_URL}/blocks/{page_id}/children"
    response = requests.get(url, headers=headers, timeout=60).json()
    return len(response['results']) == 0


def get_property(page, prop_name, prop_type):
    p = page["properties"][prop_name]
    if prop_type == "title":
        content = p["title"][0]["text"]["content"]
    elif prop_type == "rich_text":
        content = p["rich_text"][0]["text"]["content"]
    elif prop_type == "number":
        content = p["number"]
    elif prop_type == "url":
        content = p["url"]
    else:
        content = ""
    return content


def property_to_value(property_type, content):
    if property_type == "title":
        return {
            "title": [{
                "text": { "content": content }
            }]
        }
    elif property_type == "rich_text":
        return {
            "rich_text": [
                {
                    "text": {"content": content[:2000]},
                    "type": "text",
                }
            ]
        }
    elif property_type == "url":
        return {property_type: content}
    return {property_type: content}
