# How to Enrich User Data with External APIs

You can enrich user data (e.g., IP geolocation) using external APIs before storing or acting on it.

## Example: Enriching with IP Geolocation

```python
import requests

def notify_new_visitor(ip, user_agent):
    location_desc = "Unknown location"
    timezone = "Unknown"
    isp = "Unknown"
    if ip not in ("127.0.0.1", "::1", "localhost", "0.0.0.0", "Unknown IP") and ip:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,timezone,isp", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "success":
                parts = [data.get('city'), data.get('regionName'), data.get('country')]
                location_desc = ", ".join(str(p) for p in parts if p)
                timezone = data.get("timezone", "Unknown")
                isp = data.get("isp", "Unknown")
    # ... store or use enriched data ...
```
