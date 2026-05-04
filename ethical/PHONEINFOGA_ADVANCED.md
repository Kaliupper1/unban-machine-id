# 📡 Advanced PhoneInfoga Usage (2026)

Detailed documentation for advanced scanners, automation, and custom configurations within the PhoneInfoga ecosystem.

## 📡 Scanners Overview

| Scanner | Description | Setup |
|---------|-------------|-------|
| **local** | Static parsing, country detection, & carrier guessing | None |
| **numverify** | Official carrier/line type data (highly accurate) | API Key required |
| **googlesearch** | Generates advanced dorking links for footprints | None |
| **ovh** | European VoIP/landline range detection | None |

## ⚙️ Configuration & API Keys

### Numverify API Key Setup
```bash
export NUMVERIFY_API_KEY="your_api_key_here"
phoneinfoga scan -n +1234567890
```

### Custom Scanner Plugins
PhoneInfoga supports custom scanner modules compiled as Go plugins:
```bash
phoneinfoga scan -n +1234567 --plugin ./my_scanner.so
```

## 🔍 Scanning Syntax
Special characters (spaces, dashes, parens) are automatically escaped.
```bash
# All these are valid:
phoneinfoga scan -n "+1 (555) 444-1212"
phoneinfoga scan -n "+33 06 79368229"
phoneinfoga scan -n "33679368229"
```
