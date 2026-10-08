# collector/log_parser.py
# Parses the raw pasted text from the user
# Extracts sections from: uname -a, ip addr, lscpu, free -h, df -h, uptime
# Does NOT run any commands — read-only parser only

import re


def parse_raw_input(raw_text: str) -> dict:
    sections = {
        "uname":  "",
        "ip":     "",
        "lscpu":  "",
        "memory": "",
        "disk":   "",
        "uptime": "",
        "raw":    raw_text.strip()
    }

    lines = raw_text.strip().splitlines()
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        section_name = _detect_section_header(stripped)
        if section_name:
            current_section = section_name
            continue

        if _is_uname(stripped):
            current_section = "uname"
        elif _is_ip(stripped):
            current_section = "ip"
        elif _is_lscpu(stripped):
            current_section = "lscpu"
        elif _is_memory(stripped):
            current_section = "memory"
        elif _is_disk(stripped):
            current_section = "disk"
        elif _is_uptime(stripped):
            current_section = "uptime"

        if current_section:
            sections[current_section] += line + "\n"

    return sections


def _detect_section_header(line: str):
    cleaned = line.strip().lstrip("#-* ")
    cleaned = cleaned.rstrip(": ")
    if not cleaned:
        return None

    alias_map = {
        "os": "uname",
        "kernel": "uname",
        "operating system": "uname",
        "cpu": "lscpu",
        "processor": "lscpu",
        "lscpu": "lscpu",
        "memory": "memory",
        "ram": "memory",
        "mem": "memory",
        "disk": "disk",
        "storage": "disk",
        "filesystem": "disk",
        "network": "ip",
        "ip": "ip",
        "ip addr": "ip",
        "interface": "ip",
        "uptime": "uptime",
        "load average": "uptime",
    }

    normalized = cleaned.lower()
    for key in sorted(alias_map, key=len, reverse=True):
        if normalized == key or normalized.startswith(f"{key} "):
            return alias_map[key]
    return None


def _is_uname(line: str) -> bool:
    return line.lower().startswith("linux")

def _is_ip(line: str) -> bool:
    return bool(re.match(r"^\d+:\s+\w+", line))

def _is_lscpu(line: str) -> bool:
    return line.lower().startswith("architecture")

def _is_memory(line: str) -> bool:
    return line.strip().lower().startswith("total") and "used" in line.lower()

def _is_disk(line: str) -> bool:
    return line.lower().startswith("filesystem")

def _is_uptime(line: str) -> bool:
    return "load average" in line.lower()


def extract_summary(sections: dict) -> dict:
    return {
        "os":     _extract_os(sections["uname"]),
        "ip":     _extract_ip(sections["ip"]),
        "cpu":    _extract_cpu(sections["lscpu"]),
        "ram":    _extract_ram(sections["memory"]),
        "disk":   _extract_disk(sections["disk"]),
        "uptime": _extract_uptime(sections["uptime"])
    }


def _extract_os(text: str) -> str:
    lines = text.strip().splitlines()
    return lines[0].strip() if lines else "Unknown"

def _extract_ip(text: str) -> str:
    match = re.findall(r"inet\s+([\d.]+)", text)
    for ip in match:
        if not ip.startswith("127."):
            return ip
    return "Unknown"

def _extract_cpu(text: str) -> str:
    for line in text.splitlines():
        if "model name" in line.lower():
            return line.split(":")[1].strip()
    return "Unknown"

def _extract_ram(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("mem"):
            parts = line.split()
            return parts[1] if len(parts) > 1 else "Unknown"
    return "Unknown"

def _extract_disk(text: str) -> str:
    for line in text.splitlines():
        if line.endswith("/"):
            parts = line.split()
            return parts[1] if len(parts) > 1 else "Unknown"
    return "Unknown"

def _extract_uptime(text: str) -> str:
    lines = text.strip().splitlines()
    return lines[0].strip() if lines else "Unknown"