# 🤖 Social Media & Automation

Advanced scripts and techniques for mapping phone numbers to digital identities across social platforms and messaging apps.

## 🤖 Automated Scripts

### [Phunter](https://github.com/N0rz3/Phunter)
A versatile OSINT tool for identifying information tied to phone numbers.
```bash
# General identity & info gathering
python3 phunter.py -t +15551234567

# Check if number is linked to an Amazon account (Verification)
python3 phunter.py -a +15551234567

# Reverse lookup via Page Blanche (France specific)
python3 phunter.py -p +33612345678 -o results.txt

# Batch process multiple numbers from a file
python3 phunter.py -f numbers_list.txt
```

## 🔍 Automated Google Dorking
Use these search operators to uncover profiles or forum posts where the number has been indexed:

```text
"+1 555-123-4567" site:linkedin.com
"+1 555-123-4567" site:facebook.com
"+1 555-123-4567" site:instagram.com
"+1 555-123-4567" site:twitter.com
"+1 555-123-4567" site:tiktok.com
```

## 💬 Messaging App OSINT
Messaging apps provide high-fidelity identity markers (Profile Photos, Statuses, Usernames).
1. **WhatsApp**: Use `wa.me/number` or add to contacts to see profile pictures and "Last Seen" status.
2. **Telegram**: Utilize bots like `SangMata` or attempt to start a chat to see public profiles and group associations.
3. **Signal**: Check for "Signal Registered" status to identify privacy-conscious targets.

## 📁 Breach & Leak Analysis
Phone numbers are persistent identifiers in historical data breaches.
- **HaveIBeenPwned**: Search the database for phone numbers linked to major leaks (e.g., Facebook 2021 leak).
- **OSINT Industries**: Automatically cross-references numbers against billions of leaked records and online accounts.
- **DeHashed**: Professional search engine for mapping numbers to usernames and passwords found in leaks.
