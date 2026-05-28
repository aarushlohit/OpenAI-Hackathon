# Test Assets for Multimodal AI Validation

This directory contains test materials for validating Hermes-X multimodal investigation capabilities.

## Directory Structure

```
test_assets/
├── text/              # Text-based investigation samples
├── images/            # Image evidence (screenshots, documents)
├── pdfs/              # PDF documents (offer letters, contracts)
├── audio/             # Audio files (phone calls, voice notes)
├── scams/             # Known scam patterns (reference library)
└── safe/              # Legitimate offer patterns (baseline)
```

## Text Evidence

**Purpose**: Text-based threat detection (behavioral analysis + OSINT)

**Sample Files** (to be created):
- `telegram_onboarding_payment.txt` - Telegram HR message requesting payment
- `fake_internship_sop.txt` - Standard Operating Procedure from fake internship portal
- `recruiter_urgency_email.txt` - Urgency-driven recruiter message
- `phishing_portal_redirect.txt` - Suspicious redirect to payment page

**Expected Signals**:
- payment_coercion (98%+ confidence)
- telegram_impersonation (94%+ confidence)
- urgency_pressure (90%+ confidence)
- non_official_channel (95%+ confidence)

## Image Evidence

**Purpose**: Visual threat detection (OCR + artifact analysis)

**Sample Files** (to be created):
- `telegram_payment_screenshot.png` - Telegram chat showing payment request
- `upi_payment_instruction.png` - Screenshot of UPI payment interface
- `fake_offer_branding.png` - Suspicious company branding in screenshot
- `payment_proof_request.jpg` - Request to show payment proof

**Expected Artifacts**:
- payment_screenshot (92%+ confidence)
- telegram_chat_interface (91%+ confidence)
- upi_payment_instruction (96%+ confidence)
- suspicious_branding (87%+ confidence)

## PDF Evidence

**Purpose**: Document forgery detection

**Sample Files** (to be created):
- `fake_offer_letter.pdf` - Forged offer letter with payment extraction
- `suspicious_contract.pdf` - Contract with embedded payment requests
- `metadata_suspicious.pdf` - PDF with suspicious creation metadata
- `branding_inconsistency.pdf` - Document with mismatched company branding

**Expected Indicators**:
- payment_extraction_in_offer (98%+ confidence)
- branding_inconsistency (87%+ confidence)
- suspicious_metadata (73%+ confidence)
- forged_signature (81%+ confidence)

## Audio Evidence

**Purpose**: Behavioral threat detection from voice

**Sample Files** (to be created):
- `recruiter_call_payment_request.wav` - Recorded call requesting payment
- `urgency_pressure_tone.wav` - Call with artificial urgency/time pressure
- `coercive_language.wav` - Audio sample with coercive language patterns
- `payment_extraction_language.wav` - Call referencing specific payment amounts

**Expected Signals**:
- payment_extraction_language (96%+ confidence)
- urgency_pressure_tone (89%+ confidence)
- coercive_language (88%+ confidence)
- manipulation_patterns (85%+ confidence)

**Audio Specifications**:
- Format: WAV, MP3, M4A
- Duration: 15-30 seconds typical
- Sample rate: 16kHz or higher
- Transcription confidence target: >92%

## Scam Reference Library

**Purpose**: Known threat patterns for validation

**File Types**:
- JSON files with known scam indicators
- Regex patterns for threat detection
- Infrastructure signatures (domains, IPs)
- Campaign correlation templates

**Example Structure**:
```json
{
  "campaign_id": "telegram_onboarding_scams_2026",
  "threat_actors": ["@careerfastjob", "@hrquickjobs", "@internshipfast"],
  "patterns": [
    "refundable onboarding payment",
    "telegram only communication",
    "no official email",
    "urgent payment required"
  ],
  "indicators": [
    "pay@upi",
    "telegram_only_recruitment"
  ],
  "severity": "critical"
}
```

## Safe/Legitimate Reference

**Purpose**: Baseline for false positive testing

**File Types**:
- Legitimate company offer letters
- Real recruiter communications
- Standard onboarding procedures
- Official payment processes

**Expected Properties**:
- Multi-channel communication (email + LinkedIn + official portal)
- No payment requests upfront
- Official company branding
- Clear company contact information
- Professional tone and formatting

---

## Test Asset Creation Guidelines

### For Images

1. **Screenshot Convention**: Use standard mobile device size (1080x1920px)
2. **Telegram Interface**: Use accurate UI elements (simulated or real)
3. **Payment Evidence**: Clearly show payment requests and amounts
4. **Metadata**: Include capture timestamps for realism

### For PDFs

1. **Font**: Use common business fonts (Arial, Calibri, Times New Roman)
2. **Branding**: Include company headers/footers for realism
3. **Content**: Include realistic job descriptions alongside payment requests
4. **Metadata**: Set creation dates to approximate time of threat

### For Audio

1. **Quality**: Minimal background noise (simulates real recordings)
2. **Speaker**: Clear, natural speech patterns
3. **Duration**: 15-30 seconds typical for investigations
4. **Tone**: Include vocal patterns (urgency, coercion, manipulation)

### For Text

1. **Formatting**: Preserve actual message formatting (line breaks, emojis)
2. **Language**: Include multilingual content where applicable
3. **Timestamps**: Include message timing information
4. **Metadata**: Include sender information and channels

---

## Validation Workflow

### Step 1: Prepare Assets
1. Create subdirectories for each modality
2. Add sample files following guidelines
3. Document each file's purpose and expected signals

### Step 2: Run Multimodal Validation
```bash
python scripts/full_multimodal_ai_validation.py
```

### Step 3: Verify Output
- [ ] Each modality processed without errors
- [ ] Signals detected match expected patterns
- [ ] Confidence scores in expected range (85-98%)
- [ ] NVIDIA model attribution shown
- [ ] Evidence source attribution truthful

### Step 4: Persist Findings
- [ ] Investigation snapshot stored in PostgreSQL
- [ ] Deterministic hash generated and verified
- [ ] Graph intelligence populated
- [ ] Replay events all captured

---

## Coverage Matrix

| Modality | File Type | Threat Type | Expected Signal |
|----------|-----------|------------|-----------------|
| Text | TXT | Payment coercion | payment_coercion (98%) |
| Text | TXT | Channel restriction | non_official_channel (95%) |
| Image | PNG | Payment screenshot | payment_screenshot (93%) |
| Image | JPG | Telegram interface | telegram_chat_interface (91%) |
| PDF | PDF | Forged offer | payment_extraction_in_offer (98%) |
| PDF | PDF | Branding issues | branding_inconsistency (87%) |
| Audio | WAV | Coercive tone | coercive_language (88%) |
| Audio | MP3 | Payment extraction | payment_extraction_language (96%) |

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Multimodal Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python scripts/full_multimodal_ai_validation.py --json > report.json
      - run: python -c "import json; r=json.load(open('report.json')); exit(0 if r['validation_status']=='PASSED' else 1)"
      - uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: report.json
```

---

## Notes

- Test assets are for validation and demonstration purposes only
- Do not use real personally identifiable information in test data
- Maintain consistent formatting across similar evidence types
- Update assets when threat patterns evolve
- Archive old assets for historical analysis
