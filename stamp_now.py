import os, json, datetime
from notion_client import Client
from notion_client.errors import APIResponseError

# Load every env var that starts with CRED_
creds = []
for key, val in os.environ.items():
    if key.startswith("CRED_"):
        try:
            creds.append(json.loads(val))
        except json.JSONDecodeError:
            print(f"⚠️  Secret {key} has invalid JSON; skipping.")

if not creds:
    print("❌  No CRED_* secrets found. Exiting.")
    raise SystemExit(1)

# Timezone-aware UTC timestamp (avoids utcnow() deprecation + is explicit)
now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _paginate_query(query_fn, **kwargs):
    """Collect all results from a Notion paginated query endpoint."""
    results = []
    start_cursor = None
    while True:
        payload = dict(kwargs)
        if start_cursor:
            payload["start_cursor"] = start_cursor

        resp = query_fn(**payload)
        results.extend(resp.get("results", []))

        if not resp.get("has_more"):
            break
        start_cursor = resp.get("next_cursor")
        if not start_cursor:
            break

    return results


def _get_first_data_source_id(notion: Client, db_id: str) -> str:
    db = notion.databases.retrieve(database_id=db_id)
    data_sources = db.get("data_sources") or []
    if not data_sources:
        raise RuntimeError(
            "No data_sources found on this database. "
            "Make sure you're using a Notion-Version that supports data sources."
        )

    if len(data_sources) > 1:
        print(f"⚠️  DB {db_id[:8]} has {len(data_sources)} data sources; using the first one.")

    return data_sources[0]["id"]


def stamp(token: str, db_id: str, prop: str):
    notion = Client(
        auth=token,
        # Explicitly use the modern API model (data sources)
        notion_version="2025-09-03",
    )

    filter_obj = {"property": prop, "date": {"is_empty": True}}

    try:
        # Preferred path (modern): query the database's first data source
        if hasattr(notion, "data_sources") and hasattr(notion.data_sources, "query"):
            ds_id = _get_first_data_source_id(notion, db_id)
            pages = _paginate_query(
                notion.data_sources.query,
                data_source_id=ds_id,
                filter=filter_obj,
            )
        # Fallback (older SDKs): query the database directly
        else:
            pages = _paginate_query(
                notion.databases.query,
                database_id=db_id,
                filter=filter_obj,
            )
    except APIResponseError as e:
        print(f"⚠️  Could not query DB {db_id[:8]} — {e.code}: {e}")
        return
    except Exception as e:
        print(f"⚠️  Could not query DB {db_id[:8]} — {e}")
        return

    if not pages:
        print(f"ℹ️  Nothing to stamp in DB {db_id[:8]} (property “{prop}” already filled).")
        return

    for p in pages:
        try:
            notion.pages.update(
                page_id=p["id"],
                properties={prop: {"date": {"start": now_iso}}},
            )
            print(f"✅  Stamped {p['id']} in DB {db_id[:8]} via “{prop}”")
        except APIResponseError as e:
            print(f"⚠️  Could not update page {p['id']} — {e.code}: {e}")


for c in creds:
    if {"token", "db_id", "prop"} <= c.keys():
        stamp(c["token"], c["db_id"], c["prop"])
    else:
        print("⚠️  Incomplete credential object:", c)
