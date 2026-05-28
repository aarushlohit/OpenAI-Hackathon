#!/usr/bin/env python3
"""
QUICK START: Multimodal AI Proof
Run this to see Hermes-X powered by REAL NVIDIA cognition across TEXT + IMAGE + PDF + AUDIO
"""

import subprocess
import sys

def main():
    print("\n" + "="*80)
    print("HERMES-X MULTIMODAL AI PROOF — QUICK START")
    print("="*80 + "\n")
    
    print("This test proves Hermes-X is NOT a fake rule engine.")
    print("It's powered by real NVIDIA Nemotron Omni cognition across 4 modalities.\n")
    
    print("What will be tested:")
    print("  ✓ TEXT reasoning → payment_coercion detection")
    print("  ✓ IMAGE reasoning → Telegram screenshot artifact detection")
    print("  ✓ PDF reasoning → Forged offer letter detection")
    print("  ✓ AUDIO reasoning → Coercive tone detection")
    print("  ✓ Agent orchestration → Multi-agent consensus")
    print("  ✓ Hybrid verdict synthesis → 3-layer decision (AI + rule + consensus)")
    print("  ✓ Evidence persistence → Deterministic replay verification")
    print("  ✓ Graph intelligence → Campaign correlation detection\n")
    
    print("Starting validation...")
    print("(This runs in 10-30 seconds)\n")
    
    try:
        result = subprocess.run(
            ["python", "scripts/full_multimodal_ai_validation.py"],
            capture_output=False,
        )
        
        if result.returncode == 0:
            print("\n" + "="*80)
            print("✓ VALIDATION PASSED")
            print("="*80)
            print("\nHermes-X is ready for production use.")
            print("See MULTIMODAL_AI_PROOF.md for complete documentation.\n")
            return 0
        else:
            print("\n✗ Validation failed")
            return 1
            
    except Exception as e:
        print(f"\n✗ Error running validation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
