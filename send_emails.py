import pandas as pd
import yagmail
import json
import sys
from datetime import datetime

def send_emails(config):
    log_file = open("email_log.txt", "a")

    try:
        yag = yagmail.SMTP(user=config["sender_email"], password=config["sender_password"])
    except Exception as e:
        print("Login failed:", e)
        return

    try:
        df = pd.read_csv(config["csv_path"])
    except Exception as e:
        print("Error reading CSV:", e)
        return

    for idx, row in df.iterrows():
        to_email = row.get("email")
        name = row.get("name", "there")
        subject = config["subject"]
        message_body = config["message"].replace("{name}", name)

        try:
            yag.send(
                to=to_email,
                subject=subject,
                contents=[message_body],
                attachments=config["resume_path"]
            )
            status = "Sent"
        except Exception as e:
            status = f"Failed ({str(e)})"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {to_email}: {status}")
        log_file.write(f"{timestamp},{to_email},{status}\n")

    log_file.close()

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    send_emails(config)
