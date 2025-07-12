from datetime import datetime
import json

def log_event(user, event_type, metadata):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user["username"],
        "event": event_type,
        "details": metadata
    }
    with open("/Users/aarthithirumavalavan/Desktop/Job_related_UK/Scrumconnect/logs/audit_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")