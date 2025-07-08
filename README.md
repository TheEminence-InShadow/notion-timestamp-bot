# notion-timestamp-bot
For automating my Notion Archive page. That way, I can simply drag and drop pages in the Archive database, and it will automatically stamp the date and time they were archived.

Below is a documentation of everything you’re likely to forget later: how the bot works, how to add/remove databases, change the schedule, and common troubleshooting steps.

# Notion-Timestamp-Bot  
Automatically timestamps pages dropped into one (or many) Notion databases – runs 24 / 7 via GitHub Actions.

---

## ✨ What it does
1. Every **10 minutes** (cron schedule), GitHub Actions spins up a tiny runner.  
2. The runner loads every secret whose name starts with **`CRED_`**.  
3. Each secret contains a JSON blob:  
   ```json
   {"token":"secret_xxx","db_id":"abcd1234…","prop":"Date Archived"}

4. For every credential found, it:

   * Queries the database for pages whose `prop` is empty
   * Sets the property to “now” (UTC)
   * Prints `✅ Stamped …` in the Action log
5. Shuts down (you’re only billed in minutes, and public repos are unlimited 🆓).

---

## 🔐 Secrets structure

| Secret name (example) | Description                              |
| --------------------- | ---------------------------------------- |
| `CRED_ARCHIVE`        | One-line JSON blob for **one** database  |
| `CRED_CLASS_NOTES`    | Another database, same format            |
| …                     | Add as many `CRED_*` secrets as you like |

JSON **keys** (all required):

| Key     | Meaning                                  |
| ------- | ---------------------------------------- |
| `token` | Integration token for the workspace      |
| `db_id` | 32-character database ID (before `?v=`)  |
| `prop`  | Exact name of the date property to stamp |

---

## ➕ Adding a new database

1. In Notion → **Create / reuse** an internal integration (Name: Auto-Timestamp Bot) → copy its *token*.
2. Share the target database with that integration (**Share → Add connections → Can edit**).
3. Copy the DB ID (first 32 chars of the page URL).
4. Repo → **Settings → Secrets → Actions → New secret**

   * **Name:** `CRED_<whatever>` (must start with `CRED_`)
   * **Value:**

     ```json
     {"token":"secret_...","db_id":"...","prop":"Date Archived"}
     ```
5. Commit nothing! Just save the secret.
6. (Optional) **Actions → Stamp Notion dates → Run workflow** to test instantly.

---

## ➖ Removing a database

1. Delete its `CRED_<name>` secret.
2. **Edit** `.github/workflows/timestamp.yml` and remove (or comment) the matching line in the `env:` block:

   ```yaml
   # CRED_<name>: ${{ secrets.CRED_<name> }}
   ```
3. Commit the change. Next run ignores that database.

---

## ⏱ Changing the run frequency

Edit the cron line in `.github/workflows/timestamp.yml`.

| Interval | Cron expression |
| -------- | --------------- |
| 5 min    | `'*/5 * * * *'` |
| 2 min    | `'*/2 * * * *'` |
| 1 min\*  | `'* * * * *'`   |

\* GitHub allows 1-min cadence; stay considerate of API limits.

---

## 🚑 Troubleshooting

| Symptom                                     | Fix                                                                |
| ------------------------------------------- | ------------------------------------------------------------------ |
| `No CRED_* secrets found. Exiting.`         | Add at least one `CRED_…` secret **and** map it in `env:`.         |
| `Incomplete credential object`              | Ensure JSON has `token`, `db_id`, **and** `prop`.                  |
| `Secret not found: CRED_X` (workflow fails) | You removed a secret but left its `env:` line – remove/comment it. |
| `KeyError: '<prop name>'`                   | Property name in secret doesn’t match the column in Notion.        |
| `401 unauthorized` or `invalid_request`     | Token wrong or database not shared with the integration.           |

---

## 🛡 Security notes

* **Secrets** are always encrypted; never print them in logs.
* Public repo: code & logs are visible, *secrets are not*.
* Integration tokens can be revoked anytime in Notion.
