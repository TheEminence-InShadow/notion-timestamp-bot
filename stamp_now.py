import os, re, json, datetime
from notion_client import Client

# 1️⃣ Collect any secret whose name looks like CRED_<n>
creds = []
for key, val in os.environ.items():
    m = re.match(r"CRED_(\d+)$", key)
    if m:
        try:
            creds.append(json.loads(val))
        except json.JSONDecodeError:
            print(f"⚠️  Secret {key} contains invalid JSON; skipping.")

if not creds:
    print("❌  No CRED_n secrets found. Exiting.")
    raise SystemExit(1)

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
