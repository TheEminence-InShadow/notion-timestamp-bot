import os, re, json, datetime
from notion_client import Client

# Accept ANY suffix after "CRED_"
creds = []
for key, val in os.environ.items():
    if key.startswith("CRED_"):
        try:
            creds.append(json.loads(val))
        except json.JSONDecodeError:
            print(f"⚠️  Secret {key} has invalid JSON; skipping.")

if not creds:
    print("❌  No CRED_* secrets found. Exiting."); raise SystemExit(1)

now_iso = datetime.datetime.utcnow().isoformat()

def stamp(token, db_id, prop):
    notion = Client(auth=token)
    try:
        pages = notion.databases.query(
            database_id=db_id,
            filter={"property": prop, "date": {"is_empty": True}},
        )["results"]
    except Exception as e:
        print(f"⚠️  Could not query DB {db_id[:8]} — {e}")
        return
    for p in pages:
        notion.pages.update(
            page_id=p["id"],
            properties={prop: {"date": {"start": now_iso}}},
        )
        print(f"✅  Stamped {p['id']} in DB {db_id[:8]} via “{prop}”")

for c in creds:
    if {"token", "db_id", "prop"} <= c.keys():
        stamp(c["token"], c["db_id"], c["prop"])
    else:
        print("⚠️  Incomplete credential object:", c)
