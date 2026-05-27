#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SCENARIO="${1:-telegram_onboarding_scam}"

case "$SCENARIO" in
  telegram_onboarding_scam)
    INPUT="Telegram HR from @careerfastjob claims direct internship selection. Asks refundable onboarding payment of 3500. Provides UPI pay@upi. Sends URL: https://career-fasttrack-placement.xyz. Claims limited slots."
    ;;
  fake_internship_portal)
    INPUT="Verify internship onboarding at https://new-careers.xyz/verify before interview. Recruiter claims direct selection and asks Telegram-only communication."
    ;;
  forged_offer_letter)
    INPUT="Offer letter asks refundable security deposit before joining confirmation and bypasses interview process."
    ;;
  recruiter_impersonation)
    INPUT="Recruiter using hr@career-fasttrack-placement.xyz asks for documents and sends Telegram handle @careerfastjob for onboarding payment."
    ;;
  coordinated_campaign)
    INPUT="Multiple domains reuse @careerfastjob and pay@upi across cloned internship portals with limited slot pressure."
    ;;
  *)
    echo "Unknown scenario: $SCENARIO"
    echo "Available: telegram_onboarding_scam, fake_internship_portal, forged_offer_letter, recruiter_impersonation, coordinated_campaign"
    exit 1
    ;;
esac

echo "[DEMO] Scenario: $SCENARIO"
echo "[DEMO] Launching deterministic investigation"
python hermes.py investigate "$INPUT"

