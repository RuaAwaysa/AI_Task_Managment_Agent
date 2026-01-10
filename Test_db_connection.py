import os
import requests

NOTION_TOKEN = os.getenv("NOTION_INTERNAL_SECRET")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
}

res = requests.get(url, headers=headers)
print(res.status_code, res.text)
