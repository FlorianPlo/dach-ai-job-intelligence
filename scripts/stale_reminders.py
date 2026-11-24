#!/usr/bin/env python3
"""GitHub test version of the Lumos stale-task reminder.

Same logic as the Forgejo version, but reads issues from this GitHub repo.
GitHub doesn't expose assignees' emails, so all mails go to TEST_TO.

Env vars:
  GITHUB_TOKEN     provided by Actions
  GITHUB_REPOSITORY  provided by Actions, e.g. FlorianPlo/dach-ai-job-intelligence
  STALE_DAYS       default 7 (set 0 to test with fresh issues)
  TEST_TO          where all test mails go
  SMTP_HOST/PORT/USER/PASS
  OPT_OUT_ISSUE    optional issue number; anyone who reacts to it is skipped
  DRY_RUN          "true" -> print instead of sending
"""
import html
import json
import os
import smtplib
import ssl
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]
STALE_DAYS = int(os.environ.get("STALE_DAYS") or "7")
TEST_TO = os.environ["TEST_TO"]
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"
OPT_OUT_ISSUE = os.environ.get("OPT_OUT_ISSUE", "").strip()
BOARD = f"https://github.com/{REPO}/issues"


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={
        "Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def open_issues():
    page, out = 1, []
    while True:
        batch = api(f"/repos/{REPO}/issues?state=open&per_page=100&page={page}")
        if not batch:
            return [i for i in out if "pull_request" not in i]  # skip PRs
        out += batch
        page += 1


def opted_out():
    if not OPT_OUT_ISSUE:
        return set()
    return {r["user"]["login"].lower()
            for r in api(f"/repos/{REPO}/issues/{OPT_OUT_ISSUE}/reactions")}


def build_mail(login, items):
    opt_out_url = f"https://github.com/{REPO}/issues/{OPT_OUT_ISSUE}" if OPT_OUT_ISSUE else BOARD
    text = [f"Hi {login},", "",
            f"{len(items)} of your issues haven't moved in {STALE_DAYS}+ days:", ""]
    rows = ""
    for days, i in items:
        labels = ", ".join(l["name"] for l in i.get("labels") or [])
        text.append(f"- #{i['number']} {i['title']} ({days}d)  {i['html_url']}")
        rows += f"""
        <tr><td style="padding:12px 0;border-bottom:1px solid #eee">
          <a href="{i['html_url']}" style="color:#111;font-weight:600;text-decoration:none">
            #{i['number']} {html.escape(i['title'])}</a>
          <div style="color:#888;font-size:13px;margin-top:3px">
            {html.escape(labels) + ' · ' if labels else ''}{days} days without update</div>
        </td></tr>"""
    text += ["", "A short comment, moving the card or closing it is enough.",
             f"Board: {BOARD}", f"Opt out (react with any emoji): {opt_out_url}"]
    body = f"""<div style="font-family:-apple-system,Segoe UI,Arial,sans-serif;max-width:520px;
                margin:auto;color:#111;line-height:1.4">
      <h2 style="margin:0 0 4px">Hi {html.escape(login)} 👋</h2>
      <p style="color:#555;margin:0 0 16px">
        {len(items)} of your issues haven't moved in {STALE_DAYS}+ days.</p>
      <table style="width:100%;border-collapse:collapse">{rows}</table>
      <p style="color:#555;margin:20px 0">
        A short comment, moving the card or closing it is enough.</p>
      <a href="{BOARD}" style="background:#111;color:#fff;padding:10px 16px;
         border-radius:6px;text-decoration:none;font-size:14px">Open the board</a>
      <p style="color:#aaa;font-size:12px;margin-top:28px">
        Lumos task bot · weekly reminder ·
        <a href="{opt_out_url}" style="color:#aaa">opt out</a></p>
    </div>"""
    return "\n".join(text), body


def main():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=STALE_DAYS)
    skip = opted_out()
    per_user = defaultdict(list)
    for i in open_issues():
        updated = datetime.fromisoformat(i["updated_at"].replace("Z", "+00:00"))
        if updated > cutoff:
            continue
        for a in i.get("assignees") or []:
            if a["login"].lower() not in skip:
                per_user[a["login"]].append(((now - updated).days, i))

    if not per_user:
        print("No stale assigned issues.")
        return

    smtp = None
    if not DRY_RUN:
        smtp = smtplib.SMTP(os.environ.get("SMTP_HOST", "smtp.gmail.com"),
                            int(os.environ.get("SMTP_PORT", "587")))
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])

    for login, items in per_user.items():
        items.sort(key=lambda x: -x[0])
        text, body = build_mail(login, items)
        if DRY_RUN:
            print(f"=== for {login} -> {TEST_TO} ===\n{text}\n")
            continue
        msg = EmailMessage()
        msg["Subject"] = f"[Lumos] {len(items)} task(s) waiting for an update"
        msg["From"] = os.environ["SMTP_USER"]
        msg["To"] = TEST_TO
        msg.set_content(text)
        msg.add_alternative(body, subtype="html")
        smtp.send_message(msg)
        print(f"sent mail for {login} to {TEST_TO} ({len(items)} issues)")

    if smtp:
        smtp.quit()


if __name__ == "__main__":
    main()
