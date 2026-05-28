# Interactive Testing Guide - Hermes-X Custom Investigations

## Live Demo Just Ran ✅

```
Input: "Telegram HR from @careerfastjob asks refundable onboarding payment 
of 3500 via UPI pay@upi and asks onboarding through Telegram only."

Result:
  ⚠️ HIGH THREAT (Score: 78/100)
  Confidence: 84%
  Verdict: hybrid_correlation (AI + Deterministic + Consensus)
  
Breakdown:
  [1] Behavioral Analysis → 70/100 risk (3 signals: payment_extraction, non_official_channel, payment_coercion)
  [2] OSINT Analysis → 75/100 reputation (Telegram impersonation detected)
  [3] Deterministic Validation → ✓ CONFIRMED (2 checks passed)
  [4] Cross-Agent Consensus → 100% (2/2 agents agreed)
  [5] Hybrid Verdict → SYNTHESIZED
```

---

## Run Your Own Investigation

### Method 1: Interactive Console

```bash
python scripts/custom_investigation.py
```

Then paste/type your investigation input. Press Enter twice to submit.

### Method 2: With JSON Output

```bash
python scripts/custom_investigation.py --json
```

Outputs structured JSON report for parsing/integration.

### Method 3: Pipe From File

```bash
cat test_case.txt | python scripts/custom_investigation.py --json
```

### Method 4: One-liner

```bash
echo "Your suspicious message here" | python scripts/custom_investigation.py --json
```

---

## Test Cases Ready to Use

### Case 1: Payment Scam (Should be CRITICAL)
```
WhatsApp from +91-98765-43210: "Congrats! Selected for job. Need ₹2,500 
as refundable processing fee. Transfer via UPI: scammer@upi. Only message 
here for confidentiality. URGENT!"
```

Expected: **CRITICAL 🚨** (Score ~95)

### Case 2: Domain Impersonation (Should be HIGH)
```
Email from sender "hr@amazonjobs-careers.in" (not amazon.com): "Your offer 
is attached. Please confirm and send: 1) ₹3,000 advance for background 
check (refundable) 2) Photo ID 3) Bank details. Reply only to this email."
```

Expected: **HIGH ⚠️** (Score ~80)

### Case 3: Legitimate Offer (Should be LOW)
```
Email from careers@microsoft.com: "We're pleased to offer you Senior 
Software Engineer at Bangalore. Salary ₹18L/year. Start: June 15. Click 
here to accept: https://careers.microsoft.com/offer/ABC123"
```

Expected: **LOW ✓** (Score ~15)

### Case 4: Telegram Job Bot Spam (Should be MEDIUM-HIGH)
```
Telegram: "@techcareers_bot has sent you a job offer. 'Data Entry. 
₹8-12L/month. $50 training course required first. Link: identityverify.io/course. 
Limited spots, decide quickly!' Only reply in group chat."
```

Expected: **MEDIUM-HIGH ⚡** (Score ~65)

### Case 5: LinkedIn Recruiter Phish (Should be HIGH)
```
LinkedIn: "Hi! Your profile was reviewed. Perfect fit for Senior Dev role 
at Acme Tech. Please download our secure form: https://acme-secure-form.tk/download.
exe and email back your resume + photo + ID. Urgent!"
```

Expected: **HIGH ⚠️** (Score ~85)

---

## What Gets Detected

### ✅ Behavioral Signals Detected
- `payment_extraction` — Fee/payment requests
- `non_official_channel` — Restricted to Telegram/WhatsApp only
- `payment_coercion` — Refundable deposit (classic red flag)
- `urgency_pressure` — Artificial time pressure

### ✅ OSINT Signals Detected
- `newly_registered_domain` — Domain < 30 days old
- `telegram_impersonation` — Telegram-only communication
- Domain reputation analysis
- Email domain mismatches (amazonjobs.in vs amazon.com)

### ✅ Deterministic Validation
- Payment extraction confirmed by rules
- Unofficial channel rules validation
- Urgency/pressure pattern matching

### ✅ Cross-Agent Consensus
- Payment threat consensus (behavioral + deterministic)
- Channel restriction consensus (behavioral + OSINT)

---

## Output Format

### Console Output (Human-Readable)

```
[1/5] BEHAVIORAL ANALYSIS
✓ Behavioral Risk Score: 70/100
✓ Confidence: 90%
✓ Signals Detected: 3
  • payment_extraction: Payment or financial transaction requested.
  • non_official_channel: Communication restricted to unofficial channels only.
  • payment_coercion: Refundable deposit or advance payment requested.

[2/5] OSINT INTELLIGENCE
✓ Reputation Score: 75/100
✓ Confidence: 78%
✓ Indicators Found: 1
  • telegram_impersonation: Telegram used as primary communication.

[3/5] DETERMINISTIC VALIDATION
✓ Payment extraction detected and CONFIRMED
✓ Unofficial channel restriction CONFIRMED

[4/5] CROSS-AGENT CONSENSUS
✓ Payment threat consensus: 2+ layers detected
✓ Channel restriction consensus: behavioral + OSINT aligned
✓ Consensus Strength: 100% (2/2)

[5/5] HYBRID VERDICT SYNTHESIS
⚠️ VERDICT: HIGH THREAT
Score: 78/100 | Confidence: 84%
Source: hybrid_correlation
Primary Cognition: nvidia_nim
Deterministic Validation: ✓ CONFIRMED
Cross-Agent Consensus: ✓ REACHED

RECOMMENDATION:
⚠️ HIGH CAUTION. Review carefully before any engagement. 
Verify with company HR independently.
```

### JSON Output (`--json` flag)

```json
{
  "timestamp": "2026-05-27T21:12:58.378Z",
  "investigation_id": "INV-20260527",
  "input": "...",
  "verdict": {
    "final_score": 78,
    "confidence": 0.84,
    "severity": "HIGH",
    "verdict_source": "hybrid_correlation",
    "primary_cognition": "nvidia_nim",
    "deterministic_validation": true,
    "cross_agent_consensus": true
  },
  "analysis_stages": {
    "behavior": { ... },
    "osint": { ... },
    "deterministic_validation": { ... },
    "consensus": { ... }
  }
}
```

---

## Integration Points

### For Backend Systems
```bash
python scripts/custom_investigation.py --json | jq '.verdict.final_score'
# Output: 78
```

### For Batch Processing
```bash
for input in case1.txt case2.txt case3.txt; do
  echo "=== $input ==="
  cat "$input" | python scripts/custom_investigation.py --json | jq '.verdict'
done
```

### For Real Provider Integration (Phase 2)
The script currently simulates AI reasoning. To integrate with real NVIDIA/OpenAI:

1. Replace message pattern matching with actual AI provider calls
2. Update behavior_analysis agent to invoke `text_router.generate()`
3. Update osint_agent to invoke NVIDIA/OpenAI for domain intelligence
4. Connect to real PostgreSQL event store
5. Enable websocket streaming for live progress

---

## Troubleshooting

### Script Won't Start?
```bash
python --version  # Should be 3.10+
cd /home/aarush/Myoffice/Hackathons/OpenAI\ Hackathon
python scripts/custom_investigation.py
```

### JSON parsing fails?
```bash
python scripts/custom_investigation.py --json | jq .
# If this errors, JSON output is malformed
```

### Want to save investigation results?
```bash
python scripts/custom_investigation.py --json > investigation_$(date +%s).json
```

### Running many tests?
```bash
for i in {1..10}; do
  echo "Test case: $i"
  echo "Your message here" | python scripts/custom_investigation.py --json | jq '.verdict'
  echo ""
done
```

---

## What's Different From Demo?

| Aspect | Demo (`live_gui_validation.py`) | Custom (`custom_investigation.py`) |
|--------|--------------------------------|-----------------------------------|
| Input | Hardcoded test case | User provides input |
| Execution | Fast, predetermined | Real-time processing |
| Extensibility | Limited | Full pipeline |
| Use Case | Validation only | Testing + Development |
| Output | Summary | Full JSON + Reports |

---

## Next Phase: Production Integration

1. **Real Provider Calls**: Replace mock pattern detection with actual NVIDIA Nemotron API calls
2. **Event Store**: Persist investigations to PostgreSQL
3. **WebSocket Streaming**: Real-time progress events to frontend
4. **Graph Intelligence**: Map recruiter networks across investigations
5. **Autonomous Monitoring**: Continuous threat feeds

---

## Quick Reference

```bash
# Basic usage
python scripts/custom_investigation.py

# With JSON output
python scripts/custom_investigation.py --json

# Pipe from file
cat input.txt | python scripts/custom_investigation.py

# Save results
python scripts/custom_investigation.py --json > report.json

# Parse JSON
python scripts/custom_investigation.py --json | jq '.verdict.final_score'

# Batch test
echo "Your message" | python scripts/custom_investigation.py --json | jq '.verdict'
```

---

**Status**: ✅ Ready for custom testing with any recruiter communication or suspicious message.

