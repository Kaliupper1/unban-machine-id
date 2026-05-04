# دليل سير العمل الجنائي — Forensic Investigation Workflow Guide

**OSINT Investigation Toolkit** | Aligned with NIST SP 800-86

A structured 4-phase methodology for investigating harassment cases involving Egyptian phone numbers. Follow each phase sequentially — do not skip phases. Each phase has clear entry criteria, actions, and exit criteria.

---

## Overview

```
Phase 1: Initial Triage → Phase 2: Digital Footprinting → Phase 3: Identity Resolution → Phase 4: Reporting
```

| Phase | الهدف / Goal | Tools |
|-------|-------------|-------|
| 1. Initial Triage | Classify number, identify carrier | `recon_engine.py`, PhoneInfoga |
| 2. Digital Footprinting | Map digital presence | Google Dorking, Messaging Apps |
| 3. Identity Resolution | Link number to real identity | FinTech pivots, Breach databases |
| 4. Reporting | Package evidence for authorities | `vault_integrity.py`, Templates |

---

## المرحلة الأولى: الفرز الأولي — Phase 1: Initial Triage

### Entry Criteria
- A new harassing phone number has been received
- The number has not been previously investigated (check `evidence/` directory)

### Actions

1. **Validate and normalize the phone number**
   ```bash
   python3 scripts/recon_engine.py <phone_number>
   ```
   This automatically:
   - Validates the Egyptian format (+20XXXXXXXXX)
   - Runs PhoneInfoga local scanner (carrier detection, country verification)
   - Classifies line type (Mobile / Landline / VoIP)
   - Generates Google Dorking URLs for the next phase
   - Saves all output to `evidence/<number>/`

2. **Review the scan output**
   ```bash
   cat evidence/<number>/scan_output.txt
   cat evidence/<number>/report.json
   ```

3. **Classify the threat level**
   - **Mobile** (carrier identified): Standard investigation — proceed to Phase 2
   - **Landline**: Low anonymity — check business registries, proceed to Phase 2
   - **VoIP**: HIGH ANONYMITY — flag for additional scrutiny. The caller may be using a disposable number. See `VOIP_INVESTIGATION.md` for specialized techniques.
   - **Unknown carrier / Unclassified**: Possible VoIP or international relay — proceed with caution

### Exit Criteria
- [ ] Evidence directory created: `evidence/<number>/`
- [ ] Phone number classified as Mobile, Landline, or VoIP
- [ ] Carrier identified (or flagged as "unclassified carrier — possible VoIP")
- [ ] Scan output and report saved

---

## المرحلة الثانية: البصمة الرقمية — Phase 2: Digital Footprinting

### Entry Criteria
- Phase 1 complete — number is classified and scanned
- Dorking URLs generated in `evidence/<number>/dorks.txt`

### Actions

1. **Execute Google Dorking URLs**
   Open `evidence/<number>/dorks.txt` and visit each URL in a browser:
   - Facebook, LinkedIn, Instagram, Twitter/X, TikTok, Pastebin
   - Arabic forums
   - General web search

   **Document findings**: Save screenshots of any matches to `evidence/<number>/`

2. **Check messaging applications** (see `SOCIAL_MEDIA_OSINT.md`)
   - **WhatsApp**: Visit `wa.me/<number>` — check profile photo, status, last seen
   - **Telegram**: Search the number — check public profile, group memberships
   - **Signal**: Check registration status

3. **Check breach databases**
   - **HaveIBeenPwned**: Search for the phone number in known data breaches
   - **OSINT Industries**: Cross-reference against leaked records
   - **DeHashed**: Search for number-to-username mappings

4. **Save all collected evidence**
   - Screenshots: `evidence/<number>/screenshot_*.png`
   - Notes: `evidence/<number>/notes.txt`
   - After collecting, hash all evidence:
     ```bash
     python3 scripts/vault_integrity.py --investigator "Your Name"
     ```

### Exit Criteria
- [ ] All dorking URLs checked and results documented
- [ ] Messaging apps checked (WhatsApp, Telegram, Signal)
- [ ] Breach databases queried
- [ ] All evidence files saved and hashed in manifest

---

## المرحلة الثالثة: تحديد الهوية — Phase 3: Identity Resolution

### Entry Criteria
- Phase 2 complete — digital footprint collected
- Social media profiles, breach data, and messaging app profiles documented

### Actions

1. **FinTech pivot analysis** (Egyptian payment platforms — FR-014)
   - **InstaPay**: Check if the number is registered with InstaPay mobile banking
   - **Vodafone Cash**: Attempt a small transfer to the number — the recipient's name may be revealed
   - **Orange Money / Etisalat Cash / WE Pay**: Similar checks for other Egyptian mobile payment services
   - **Fawry**: Check if the number has been used for bill payments

   > **Legal note**: Only use payment platform lookups for passive information gathering. Do not complete any financial transactions.

2. **Cross-reference breach data**
   - Correlate usernames found in breaches with social media profiles
   - Map email addresses to phone numbers using reverse lookup
   - Check if the same username appears across multiple platforms

3. **Username correlation**
   - If a username was discovered in Phase 2, search for it across:
     - Social media platforms (Facebook, Twitter, Instagram, TikTok)
     - Forums and community sites
     - Code repositories (GitHub, GitLab)
     - Gaming platforms

4. **Escalation paths** (if OSINT yields zero results)
   - Prepare a formal request for the Egyptian Cybercrime Unit with collected evidence
   - Document the subpoena requirements for carrier records (Vodafone, Orange, Etisalat, WE)
   - If the number is VoIP: request records from the VoIP provider (Twilio, Vonage, etc.)
   - Contact the ISP if IP-based evidence is available

### Exit Criteria
- [ ] Real identity linked to the number, OR
- [ ] Escalation path identified and documented (carrier subpoena, ISP request)
- [ ] All identity resolution evidence collected and hashed

---

## المرحلة الرابعة: إعداد التقارير — Phase 4: Reporting

### Entry Criteria
- Phase 3 complete — identity resolved or escalation path documented
- All evidence files collected in `evidence/<number>/`

### Actions

1. **Hash and verify all evidence**
   ```bash
   python3 scripts/vault_integrity.py --investigator "Your Name"
   python3 scripts/vault_integrity.py --verify
   ```

2. **Generate verification certificate**
   The `--verify` command automatically creates `evidence/verification_certificate.txt`

3. **Prepare the formal report**
   Use the template below to format findings for the Egyptian Cybercrime Unit.

4. **Compile the evidence package**
   - `evidence/<number>/report.json` — Machine-readable scan data
   - `evidence/<number>/report.md` — Human-readable report (Arabic/English)
   - `evidence/manifest.json` — Chain of custody with SHA-256 hashes
   - `evidence/verification_certificate.txt` — Integrity verification
   - All screenshots, logs, and notes

---

### نموذج التقرير — Report Template for Egyptian Cybercrime Unit

```
═══════════════════════════════════════════════════════════
  بلاغ جريمة إلكترونية — Cybercrime Report
  وحدة مكافحة الجرائم الإلكترونية — Egyptian Cybercrime Unit
═══════════════════════════════════════════════════════════

رقم البلاغ / Report ID: [AUTO-GENERATED UUID]
التاريخ / Date: [YYYY-MM-DD]
المحقق / Investigator: [NAME]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. ملخص الواقعة — Incident Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  رقم الهاتف المتحرش / Harassing Number: [+20XXXXXXXXX]
  نوع الخط / Line Type: [Mobile / Landline / VoIP]
  شركة الاتصالات / Carrier: [Carrier Name]
  تاريخ بدء التحرش / Harassment Start Date: [YYYY-MM-DD]
  عدد الاتصالات / Number of Contacts: [COUNT]
  طبيعة التحرش / Nature of Harassment: [DESCRIPTION]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  2. نتائج التحقيق — Investigation Findings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  2.1 تحليل الرقم / Number Analysis:
      [PhoneInfoga scan results summary]

  2.2 البصمة الرقمية / Digital Footprint:
      [Social media profiles, messaging app results]

  2.3 تحديد الهوية / Identity Resolution:
      [FinTech pivots, breach data, username correlations]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  3. الأدلة المرفقة — Attached Evidence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [List of evidence files with SHA-256 hashes from manifest.json]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  4. التوصيات — Recommendations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Recommended actions: carrier subpoena, ISP records, arrest warrant, etc.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  التوقيع / Signature: ___________________
  التاريخ / Date: ___________________
═══════════════════════════════════════════════════════════
```

### Exit Criteria
- [ ] All evidence hashed and verified (manifest.json + verification_certificate.txt)
- [ ] Formal report prepared using the template above
- [ ] Evidence package compiled and ready for submission

---

## قائمة الإجراءات التالية — Next Actions Checklist

After completing all four phases, review this checklist:

### Verification Steps
- [ ] Re-run `vault_integrity.py --verify` to confirm no evidence has been modified since collection
- [ ] Cross-check all SHA-256 hashes in the manifest against independent hash computation
- [ ] Verify all timestamps in the report are accurate

### Follow-Up Actions
- [ ] Submit formal report to the Egyptian Cybercrime Unit (if identity resolved)
- [ ] File a carrier records subpoena (if identity not resolved)
- [ ] Request ISP logs (if VoIP number traced to an IP address)
- [ ] Monitor for further harassment from the same or related numbers
- [ ] Set up call blocking / reporting with the carrier

### Evidence Retention
- [ ] Archive the complete `evidence/<number>/` directory to secure storage
- [ ] Maintain chain-of-custody documentation (manifest.json) alongside archived evidence
- [ ] Retain evidence for the duration required by Egyptian legal proceedings (minimum 3 years recommended)
- [ ] Do NOT delete evidence directories until the case is formally closed

---

*دليل سير العمل هذا مبني على معايير NIST SP 800-86 لجمع الأدلة الرقمية*
*This workflow guide is aligned with NIST SP 800-86 digital evidence collection standards*
