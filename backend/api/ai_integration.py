# api/ai_integration.py
# Sends parsed output to the OpenAI API
# Returns compliance results as structured JSON
# No model training — OpenAI is called as an external API only

import json
import traceback
import google.generativeai as genai
from config import Config

print(f"[AI] model={Config.AI_MODEL} key={bool(Config.GEMINI_API_KEY)} len={len(Config.GEMINI_API_KEY)}")
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel(Config.AI_MODEL)


def analyze_compliance(sections: dict, summary: dict) -> dict:
    prompt = _build_prompt(sections, summary)
    try:
        response = model.generate_content(prompt)
        return _parse_response(response.text)
    except Exception as e:
        traceback.print_exc()
        return {
            "items":   [],
            "summary": "AI unavailable — server may be offline. Please try again during the next online window.",
            "raw":     str(e),
            "error":   str(e)
        }


def _build_prompt(sections: dict, summary: dict) -> str:
    return f"""You are a system compliance checker. Analyze the following Linux system output and check compliance for each item below.

## System Output

### OS / Kernel (uname -a)
{sections.get("uname", "Not provided")}

### CPU (lscpu)
{sections.get("lscpu", "Not provided")}

### Memory (free -h)
{sections.get("memory", "Not provided")}

### Disk (df -h)
{sections.get("disk", "Not provided")}

### Network (ip addr)
{sections.get("ip", "Not provided")}

### Uptime
{sections.get("uptime", "Not provided")}

## Compliance Rules
1. OS: Is the Linux kernel version 5.10 or above?
2. OS: Is the OS a recognized stable release (Debian, Ubuntu, Raspberry Pi OS)?
3. CPU: Is the CPU architecture 64-bit (aarch64 or x86_64)?
4. CPU: Is the CPU load average below 80% capacity?
5. Memory: Is total RAM 1GB or above?
6. Memory: Is used memory below 90% of total?
7. Disk: Is the root partition size 8GB or above?
8. Disk: Is disk usage below 80% of total capacity?
9. Network: Does the system have a valid non-loopback IP address?
10. Uptime: Has the system been running for more than 1 minute (stable boot)?

## Instructions
Return ONLY a valid JSON object. No explanation, no markdown, no code fences.

{{
  "items": [
    {{
      "category": "OS",
      "label": "Kernel version 5.10 or above",
      "value": "<actual value found>",
      "compliant": 1,
      "suggestion": ""
    }}
  ],
  "summary": "<2-3 sentence plain-language summary>"
}}

Rules:
- compliant must be 1 or 0 only
- suggestion must be "" when compliant is 1
- suggestion must be specific and actionable when compliant is 0
- value must be the actual value from the output
- Return all 10 items in order
"""


def _parse_response(raw: str) -> dict:
    try:
        clean = raw.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        clean = clean.strip()
        data = json.loads(clean)
        return {
            "items":   data.get("items", []),
            "summary": data.get("summary", "No summary available."),
            "raw":     raw
        }
    except Exception as e:
        return {
            "items":   [],
            "summary": "AI response could not be parsed. Please try again.",
            "raw":     raw,
            "error":   str(e)
        }