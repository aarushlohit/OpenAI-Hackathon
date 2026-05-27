#!/usr/bin/env bash
# =============================================================================
# HERMES-X Demo Mode — Cinematic Scenario Launcher
# =============================================================================
# Usage:  ./scripts/demo_mode.sh [scenario]
#
# Scenarios:
#   telegram_onboarding_scam   (default)
#   fake_internship_portal
#   forged_offer_letter
#   recruiter_impersonation
#   coordinated_campaign
#   fake_portal_attack
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}") /.." && pwd)"
cd "$ROOT_DIR"

SCENARIO="${1:-telegram_onboarding_scam}"

# ── Cinematic header ──────────────────────────────────────────────────────────
cat <<'BANNER'

  ██╗  ██╗███████╗██████╗ ███╗   ███╗███████╗███████╗    ██╗  ██╗
  ██║  ██║██╔════╝██╔══██╗████╗ ████║██╔════╝██╔════╝    ╚██╗██╔╝
  ███████║█████╗  ██████╔╝██╔████╔██║█████╗  ███████╗     ╚███╔╝
  ██╔══██║██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══╝  ╚════██║     ██╔██╗
  ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║███████╗███████║    ██╔╝ ██╗
  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝    ╚═╝  ╚═╝

  AUTONOMOUS CYBER INVESTIGATION RUNTIME
  Replay Engine: ACTIVE | Graph Intelligence: LIVE | Providers: CONNECTED
BANNER

echo ""
echo "  [HERMES-X] Scenario: $SCENARIO"
echo "  [HERMES-X] Runtime: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "  [HERMES-X] Doctrine: Events define reality. Replay reconstructs cognition."
echo ""

# ── Scenario definitions ──────────────────────────────────────────────────────
case "$SCENARIO" in
  telegram_onboarding_scam)
    LABEL="Telegram Onboarding Scam"
    INPUT="Telegram HR from @careerfastjob claims direct internship selection. \
Asks refundable onboarding payment of 3500. Provides UPI pay@upi. \
Sends URL: https://career-fasttrack-placement.xyz. Claims limited slots. \
Urgency: only 3 spots remaining. No interview. Telegram-only onboarding."
    ;;
  fake_internship_portal)
    LABEL="Fake Internship Portal"
    INPUT="Verify internship onboarding at https://new-careers.xyz/verify before interview. \
Recruiter claims direct selection and asks Telegram-only communication. \
Portal registration requires payment gateway before document upload."
    ;;
  forged_offer_letter)
    LABEL="Forged Offer Letter"
    INPUT="Offer letter requires refundable security deposit of INR 5000 before joining \
confirmation and bypasses interview process. HR email from hr@infosys-careers-rpo.xyz. \
Letter requests Aadhaar scan and payment within 24 hours."
    ;;
  recruiter_impersonation)
    LABEL="Recruiter Impersonation"
    INPUT="Recruiter using hr@career-fasttrack-placement.xyz asks for documents and \
sends Telegram handle @careerfastjob for onboarding payment. Claims to represent \
TCS/Wipro. Domain registered 8 days ago. No DKIM/SPF. Urgency pressure."
    ;;
  coordinated_campaign)
    LABEL="Coordinated Campaign"
    INPUT="Multiple domains reuse @careerfastjob and pay@upi across cloned internship \
portals with limited slot pressure. Domains: career-fasttrack-placement.xyz, \
new-careers.xyz, infotech-internship-portal.xyz all share same UPI ID pay@upi \
and Telegram handle @careerfastjob. Pattern suggests coordinated campaign."
    ;;
  fake_portal_attack)
    LABEL="Fake Portal Attack"
    INPUT="Suspicious internship portal https://campus-place-tech.xyz impersonates \
FAANG-style hiring UI. Requires phone OTP, Aadhaar, bank account for 'stipend setup'. \
Domain registered 15 days ago. Invalid TLS certificate. No corporate registration. \
Social graph shows same operators as known scam campaigns."
    ;;
  *)
    echo "  [ERROR] Unknown scenario: $SCENARIO"
    echo ""
    echo "  Available scenarios:"
    echo "    telegram_onboarding_scam   — Payment coercion + Telegram onboarding"
    echo "    fake_internship_portal     — Phishing portal with payment gate"
    echo "    forged_offer_letter        — HR impersonation + document extraction"
    echo "    recruiter_impersonation    — Brand impersonation + urgency"
    echo "    coordinated_campaign       — Cross-domain campaign correlation"
    echo "    fake_portal_attack         — FAANG impersonation + credential harvest"
    exit 1
    ;;
esac

echo "  [SCENARIO] $LABEL"
echo "  [INPUT] ${INPUT:0:80}…"
echo ""
echo "  ══════════════════════════════════════════════════════════"
echo "  Launching autonomous investigation pipeline…"
echo "  ══════════════════════════════════════════════════════════"
echo ""

python hermes.py investigate "$INPUT"

echo ""
echo "  ══════════════════════════════════════════════════════════"
echo "  [HERMES-X] Investigation complete. Replay available."
echo "  [HERMES-X] Graph projected. Evidence archived."
echo "  ══════════════════════════════════════════════════════════"
