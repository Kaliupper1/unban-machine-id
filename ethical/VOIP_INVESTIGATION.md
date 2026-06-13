# 🕵️ VoIP vs Landline Tracing

Technical guide for identifying, classifying, and investigating different phone number types (Landline, Mobile, VoIP).

## 📊 Comparison Table

| Feature | Landline | Mobile | VoIP (Virtual) |
|---------|----------|--------|----------------|
| **Origin** | Physical Exchange | Cell Tower | Internet Protocol (IP) |
| **Traceability** | **High** (Fixed Address) | **Medium** (Carrier Logs) | **Low** (VPN/Proxy/Cloud) |
| **Anonymity** | Very Low | Low | **High** |
| **Common Providers** | AT&T, BT, Orange | Verizon, T-Mobile | Twilio, Vonage, Google Voice |
| **Verification Risk** | Low | Low | **High** (Robocalls/Spoofing) |

---

## 🕵️ Investigation Techniques

### 1. Classification & Identification
Use the `Numverify` API or `Twilio Lookup API` to extract the `line_type` attribute.
- **Red Flag**: If the carrier is identified as **"Twilio"**, **"TextNow"**, or **"Bandwidth"**, the number is almost certainly a disposable or virtual VoIP number.
- **OVH Detection**: Use specialized scanners to detect European VoIP ranges (often used in business or high-volume automated services).

### 2. Geolocation Analysis
- **Landlines**: Area codes and prefixes (Exchange Codes) are highly accurate for identifying physical city-level locations.
- **VoIP**: Area codes are arbitrary. A user in Tokyo can easily register a New York (+1 212) VoIP number. Geolocation of VoIP numbers should be treated with extreme skepticism.

### 3. Footprint & Reputation Analysis
- **Spam Tracking**: VoIP numbers are frequently recycled for automated spam campaigns. Check reputation on `Spamcalls.net`, `Truecaller`, or `ShouldIAnswer`.
- **Business Registries**: Landlines often appear in legacy business registries, white pages, and yellow pages, providing a link to physical entities.

---

## 🛠️ Automated Tools for Type Detection

- **PhoneInfoga (OVH Scanner)**: Targets specific European VoIP infrastructure.
- **Phunter (-t flag)**: Provides instant line type classification in terminal results.
- **Twilio CLI**: Powerful command-line tool for professional-grade number lookup:
  ```bash
  twilio phone-numbers:lookup --phone-number +15551234567 --type carrier
  ```
- **PhoneValidator**: Web interface for quick manual verification of line types.
