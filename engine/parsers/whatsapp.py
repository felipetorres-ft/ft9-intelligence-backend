import re

class WhatsAppParser:
    PATTERN = r'\[(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2})\] ([^:]+): (.+)'

    def parse_line(self, line):
        m = re.match(self.PATTERN, line)
        if not m: return None
        ts, sender, content = m.groups()
        return {"timestamp": ts, "sender": sender, "content": content, "message_type": "text"}
