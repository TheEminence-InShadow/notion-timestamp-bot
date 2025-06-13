import os, json, datetime, sys
from notion_client import Client

# 1️⃣  Load JSON string from the new secret
raw_creds = os.getenv("CREDENTIALS")
if not raw_creds:
    print("❌  CREDENTIALS secret is missing"); sys.exit(1)

try:
    CREDS = json.loads(raw_creds)
except json.JSONDecodeError as e:
    print("❌  CREDENTIALS secret is not valid JSON:", e); sys.exit(1)

now_iso = datetime.datetime.utcnow().isoformat()

def stamp_database(token: str, db_id: str, prop: str):
    notion = Client(auth=token)
    try:
        pages = notion.databases.query(
            **{
                "database_id": db_id,
                "filter": {"property": prop, "date": {"is_empty": True}},
            }
        )["results"]
    except Exception as e:
        print(f"⚠️  Skipping db {db_id[:8]}… — {e}")
        return
    for p in pages:
        notion.pages.update(
            page_id=p["id"],
            properties={prop: {"date": {"start": now_iso}}},
        )
        print("✅  Stamped", p["id"], "in DB", db_id[:8])

for entry in CREDS:
    stamp_database(entry["token"], entry["db_id"], entry["date_prop"])
