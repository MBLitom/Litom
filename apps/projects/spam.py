import re
from collections import Counter


def detect_project_request_spam(cleaned_data, honeypot_value=""):
    reasons = []
    if honeypot_value:
        reasons.append("honeypot")

    full_name = cleaned_data.get("full_name", "").strip().lower()
    email = cleaned_data.get("email", "").strip().lower()
    company = cleaned_data.get("company", "").strip().lower()
    message = cleaned_data.get("message", "").strip()
    message_lower = message.lower()

    if full_name == "test" or email == "test" or company == "test":
        reasons.append("test_identity")

    compact_message = re.sub(r"\s+", "", message_lower)
    if compact_message in {"test", "testtest", "testtesttest", "testtesttesttest"} or "testtesttest" in compact_message:
        reasons.append("test_message")

    if re.search(r"(.)\1{9,}", message_lower):
        reasons.append("repeated_characters")

    words = re.findall(r"[a-z0-9]{3,}", message_lower)
    if len(words) >= 8:
        word, count = Counter(words).most_common(1)[0]
        if count >= 6 or count / len(words) > 0.55:
            reasons.append(f"repeated_word:{word}")

    return reasons
