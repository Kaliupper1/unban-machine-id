# 📱 Phone Number OSINT Framework 2026

A professional and comprehensive guide to phone number investigation tools, frameworks, and methodologies for 2026.

---

## 🚀 Core Frameworks

### [PhoneInfoga](https://github.com/sundowndev/phoneinfoga)
The leading open-source framework for international phone number intelligence.
- **Capabilities**: International number scanning, carrier detection, line type identification (mobile/landline/VoIP), social media footprint discovery.
- **Architecture**: Go-based with REST API + Vue.js web client.
- **Deployment**: Stateless (no persistent storage required).

### [Phunter](https://github.com/N0rz3/Phunter)
Specialized tool for account linkage and social media discovery.
- **Features**: Amazon account check, social media presence, French Page Blanche lookup.

---

## 🛠️ Tooling & Installation (Kali Linux 2026)

### PhoneInfoga (Recommended)
```bash
# Docker setup (Stateless & Recommended)
docker run --rm -it -p 8080:8080 sundowndev/phoneinfoga serve -p 8080

# Binary installation
curl -sSL https://raw.githubusercontent.com/sundowndev/phoneinfoga/master/install.sh | bash
```

### Phunter Setup
```bash
git clone https://github.com/N0rz3/Phunter.git
cd Phunter && pip3 install -r requirements.txt
# Note: Requires ChromeDriver or GeckoDriver for Selenium automation.
```

### Specialized Tools
- **email2phonenumber**: Pivot from email addresses to digits.
- **PhoneValidator**: Fast line type verification (Landline/Mobile/VoIP).
- **OSINT Industries**: Professional API-driven dashboard for deep identity mapping.
- **HaveIBeenPwned**: Check if phone numbers appear in historical data breaches.

## 🔍 Investigation Workflow
Refer to the specialized guides for in-depth technical procedures:
1. **Static Analysis**: Identifies country, formats, and initial footprints (See `PHONEINFOGA_ADVANCED.md`).
2. **Line Validation**: Verifies **VoIP, Landline, or Mobile** types (See `VOIP_INVESTIGATION.md`).
3. **Identity Mapping**: Executes social media and messaging app lookups (See `SOCIAL_MEDIA_OSINT.md`).
4. **Leak Analysis**: Checks historical data breaches and account linkages.

---

## 🌐 Investigation Protocol
This framework outlines standard operating procedures for phone number intelligence. Always maintain operational security (OPSEC) and follow data protection protocols.

---

## 🔧 OSINT Investigation Toolkit

Automated CLI scripts for streamlined phone number OSINT investigations targeting Egyptian harassment cases.

### Quick Start

```bash
cd ethical/

# 1. Check your environment
python3 scripts/setup_env.py

# 2. Run a phone number reconnaissance
python3 scripts/recon_engine.py +201201796383

# 3. Hash evidence files for chain of custody
python3 scripts/vault_integrity.py --investigator "Your Name"

# 4. Verify evidence integrity
python3 scripts/vault_integrity.py --verify
```

### Usage

#### Run a phone number reconnaissance

```bash
python3 scripts/recon_engine.py +201201796383
```

This creates `evidence/+201201796383/` with:
- `scan_output.txt` — PhoneInfoga scan results
- `dorks.txt` — Google Dorking URLs for social media search
- `report.json` — Structured scan summary
- `report.md` — Human-readable report (Arabic/English)

#### Hash evidence files for chain of custody

```bash
python3 scripts/vault_integrity.py --investigator "Your Name"
```

This creates/updates `evidence/manifest.json` with SHA-256 hashes for all evidence files.

#### Verify evidence integrity

```bash
python3 scripts/vault_integrity.py --verify
```

This checks all files against the manifest and flags any modifications or new files.

#### Follow the investigation workflow

Open `WORKFLOW_GUIDE.md` for the complete 4-phase process:
1. Initial Triage → 2. Digital Footprinting → 3. Identity Resolution → 4. Reporting

### Testing

```bash
cd ethical/
python3 -m pytest tests/ -v
```

### Project Layout

```
ethical/
├── scripts/
│   ├── recon_engine.py      # Phone recon automation (P1)
│   ├── vault_integrity.py   # Evidence hashing & manifest (P2)
│   ├── setup_env.py         # Environment validation (P4)
│   ├── validators.py        # Phone number validation
│   ├── dork_generator.py    # Google Dorking URL generation
│   ├── phoneinfoga_runner.py # PhoneInfoga integration
│   ├── evidence_manager.py  # Evidence directory management
│   ├── report_writer.py     # Dual-output report writer
│   └── utils.py             # Shared utilities
├── evidence/                # Evidence storage (gitignored)
├── tests/                   # Test suite
│   ├── test_validators.py
│   ├── test_vault.py
│   ├── test_recon.py
│   └── test_setup.py
├── WORKFLOW_GUIDE.md        # 4-phase forensic investigation guide
├── PHONEINFOGA_ADVANCED.md  # PhoneInfoga reference
├── SOCIAL_MEDIA_OSINT.md    # Social media OSINT reference
├── VOIP_INVESTIGATION.md    # VoIP investigation reference
└── requirements.txt         # Python dependencies
```
