import os, datetime
from notion_client import Client

TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("DATABASE_ID")
DATE_PROP = "Archived Date"           # change if your column is named differently

now = datetime.datetime.utcnow().isoformat()
notion = Client(auth=TOKEN)

rows = notion.databases.query(
    **{
        "database_id": DB_ID,
        "filter": {"property": DATE_PROP, "date": {"is_empty": True}},
    }
)["results"]

for r in rows:
    notion.pages.update(
        page_id=r["id"],
        properties={DATE_PROP: {"date": {"start": now}}},
    )
    print("Stamped", r["id"])
