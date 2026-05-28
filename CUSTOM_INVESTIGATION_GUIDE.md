# Custom Investigation Guide

Run real investigations through Hermes-X with your own input.

## Quick Start

```bash
python scripts/custom_investigation.py
```

Then enter your investigation input (recruiter message, suspicious job offer, etc.).

### With JSON Output

```bash
python scripts/custom_investigation.py --json
```

---

## Example Test Cases

### 1. Classic Payment Scam
```
Telegram HR recruiter @techcareers2024 says:
"Hi! Congratulations on being selected. We need a ₹2,500 refundable processing fee to activate 
your offer. Transfer to UPI: pay@upi. Confirm ASAP or we give to next candidate. Only communicate 
on this Telegram for security."
```

**Expected Result:**
- Behavior Risk: HIGH (payment + urgency + official channel restriction)
- OSINT: NEW domain (days old) + no official email
- Consensus: 2/2 agreement
- **Verdict: CRITICAL 🚨**

---

### 2. Impersonation with Document Forgery
```
Email from "hr@amazonjobs.in" (but not amazon.com):
"Congratulations! Your offer letter is attached. Please confirm receipt and send:
1. A ₹5,000 advance for background check (refundable)
2. Photo ID
3. Bank details

AWS verification number is #VF-82849. Don't share with anyone else.

Reply only to this email. External communication channels are not monitored."
```

**Expected Result:**
- Behavior Risk: HIGH (payment + document pressure + fake verification code)
- OSINT: Domain impersonation (amazonjobs.in vs amazon.com)
- Deterministic: Advance payment + credential harvesting detected
- **Verdict: HIGH ⚠️**

---

### 3. Legitimate Job Offer (Should Be Low Risk)
```
Email from careers@microsoft.com:
"Dear Candidate,

We're pleased to offer you a position as Senior Software Engineer at our Bangalore office.
  
Offer Details:
- Position: Senior Software Engineer
- Location: Bangalore, India
- Base Salary: ₹18,00,000 per annum
- Start Date: June 15, 2026

Please confirm your acceptance by clicking the link below:
https://careers.microsoft.com/offer/accept/ABC123

Our HR team will contact you with next steps.

Best regards,
Microsoft Hiring Team"
```

**Expected Result:**
- Behavior Risk: LOW (no payment, official communication, standard offer)
- OSINT: Official domain (microsoft.com), valid SSL
- Deterministic: No fraud indicators
- **Verdict: LOW ✓**

---

### 4. Partial Scam (Mixed Signals)
```
LinkedIn recruiter message from @john_tech_recruiter:
"Hi! Saw your profile and think you're perfect for our new venture. We're hiring aggressively 
for blockchain dev roles. Salary ₹12-15L. 

Now, we need to verify your identity and commitment. Please purchase this $50 training course 
first - we'll reimburse after you join.

Link: https://identityverify-course.io/buy

Let me know ASAP!"
```

**Expected Result:**
- Behavior Risk: MEDIUM-HIGH (payment + time pressure + new venture)
- OSINT: Suspicious domain (identityverify-course.io)
- Consensus: Partial agreement (payment threat confirmed, but official channels exist)
- **Verdict: MEDIUM ⚡**

---

### 5. WhatsApp Onboarding Scam
```
WhatsApp message from +91-98765-43210:
"Hi! You've been selected for our Data Entry Officer role. Congratulations!

To proceed, you need to:
1. Pay ₹3,000 for training materials kit (COD or UPI)
2. Only WhatsApp communication for confidentiality
3. Confirm within 2 hours or position goes to next candidate

UPI: scammer@upi
WhatsApp: +91-98765-43210

Details: https://data-entry-jobs.tk/offer"
```

**Expected Result:**
- Behavior Risk: CRITICAL (payment + urgency + unofficial channel + fake scarcity)
- OSINT: Free hosting domain (.tk), no SSL, new registration
- Deterministic: All red flags confirmed
- **Verdict: CRITICAL 🚨**

---

## Understanding the Output

### Verdict Severity Levels

| Severity | Score | Action |
|----------|-------|--------|
| 🚨 CRITICAL | 80-100 | Do not proceed. Escalate immediately. |
| ⚠️ HIGH | 60-79 | High caution. Verify independently. |
| ⚡ MEDIUM | 40-59 | Medium caution. Investigate further. |
| ✓ LOW | 0-39 | Likely safe. Monitor for updates. |

### Verdict Source Attribution

- **🧠 AI Reasoning**: NVIDIA Nemotron detected behavioral patterns
- **🛡️ Deterministic Validation**: Rules-based system confirmed findings
- **🔀 Hybrid Correlation**: AI + deterministic + consensus alignment

### Confidence Score

Shows how confident the system is in its analysis:
- 95%+ = Very high confidence, strong evidence
- 80-95% = High confidence, multiple signals aligned
- 60-80% = Moderate confidence, requires manual review
- <60% = Low confidence, inconclusive

---

## Investigation Pipeline Stages

1. **Behavioral Analysis** 
   - Detects urgency, payment requests, channel restrictions
   - Analyzes communication patterns for coercion

2. **OSINT Intelligence**
   - Extracts domains, emails, Telegram handles
   - Evaluates reputation, domain age, SSL validity

3. **Deterministic Validation**
   - Confirms findings via rule-based checks
   - Validates against known scam patterns

4. **Cross-Agent Consensus**
   - Computes agreement across analysis layers
   - Escalates only when multiple signals align

5. **Hybrid Verdict**
   - Combines all sources with proper weighting
   - Generates explainable, traceable verdict

---

## Tips for Realistic Testing

1. **Copy real messages** from suspicious job offers you've received
2. **Test with partial information** — system should handle incomplete data
3. **Mix legitimate with fraudulent** — helps validate false positive rates
4. **Use different languages/domains** — Telegram, WhatsApp, email, LinkedIn, etc.

---

## Output Files

- **Console**: Real-time investigation progress
- **JSON Output** (with `--json`): Machine-readable report with all signals, scores, and decisions

```json
{
  "investigation_id": "INV-20260528123456",
  "final_score": 87,
  "confidence": 0.915,
  "severity": "HIGH",
  "verdict_source": "hybrid_correlation",
  "analysis_stages": {
    "behavior": {...},
    "osint": {...},
    "deterministic_validation": {...},
    "consensus": {...}
  }
}
```

---

## Debugging

Run with detailed logging:

```bash
python -u scripts/custom_investigation.py 2>&1 | tee investigation.log
```

This captures all stages and signals to `investigation.log`.

---

## Next Steps

After testing with custom input:

1. Validate against known scams in your region
2. Test with fresh job offer messages
3. Export JSON reports for integration with other systems
4. Review false positives to tune deterministic rules
5. Deploy to production with live provider integrations

