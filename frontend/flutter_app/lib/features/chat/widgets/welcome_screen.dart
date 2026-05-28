import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Welcome/empty state screen — shown before first message.
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({required this.onSuggestion, super.key});
  final void Function(String text) onSuggestion;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 580),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: cs.primary.withValues(alpha: 0.1),
                  border: Border.all(color: cs.primary.withValues(alpha: 0.3)),
                ),
                child: Icon(Icons.shield_outlined, size: 30, color: cs.primary),
              )
                  .animate()
                  .fadeIn(duration: 500.ms)
                  .scale(begin: const Offset(0.8, 0.8)),
              const SizedBox(height: 20),

              Text(
                'Hermes-X',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: cs.primary,
                      fontWeight: FontWeight.bold,
                      letterSpacing: -0.5,
                    ),
              ).animate().fadeIn(delay: 100.ms, duration: 400.ms),

              const SizedBox(height: 8),

              Text(
                'AI-powered cyber fraud investigation.\nPaste a recruiter message, upload a screenshot, or ask anything.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 15,
                  color: cs.onSurface.withValues(alpha: 0.5),
                  height: 1.5,
                ),
              ).animate().fadeIn(delay: 200.ms, duration: 400.ms),

              const SizedBox(height: 40),

              // Suggestion pills
              Wrap(
                spacing: 10,
                runSpacing: 10,
                alignment: WrapAlignment.center,
                children: _suggestions
                    .asMap()
                    .entries
                    .map(
                      (e) => _SuggestionChip(
                        label: e.value.label,
                        onTap: () => onSuggestion(e.value.text),
                      )
                          .animate(delay: Duration(milliseconds: 300 + e.key * 80))
                          .fadeIn(duration: 350.ms)
                          .slideY(begin: 0.1),
                    )
                    .toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Suggestion {
  const _Suggestion(this.label, this.text);
  final String label;
  final String text;
}

const _suggestions = [
  _Suggestion(
    '🚨 Telegram recruiter scam',
    'Telegram HR @careerfastjob claims direct Google internship selection. Asks refundable onboarding payment of ₹3500. UPI: pay@upi. URL: https://career-fasttrack-placement.xyz. Limited slots, respond within 24 hours.',
  ),
  _Suggestion(
    '🔎 Verify internship website',
    'Please verify this internship onboarding link: https://new-careers.xyz/verify — recruiter claims direct selection bypassing interviews, Telegram-only communication.',
  ),
  _Suggestion(
    '📄 Check offer letter',
    'Offer letter from hr@infosys-careers-rpo.xyz requires a refundable security deposit of ₹2000 before joining. They claim it covers background verification. Is this legitimate?',
  ),
  _Suggestion(
    '✅ Google offer legit?',
    'I received a Google internship offer through careers.google.com after 3 rounds of interviews. The HR email is from google.com. The offer letter has no payment requests. Is this legitimate?',
  ),
];

class _SuggestionChip extends StatelessWidget {
  const _SuggestionChip({required this.label, required this.onTap});
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
        decoration: BoxDecoration(
          color: cs.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: cs.onSurface.withValues(alpha: 0.1)),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 13,
            color: cs.onSurface.withValues(alpha: 0.7),
          ),
        ),
      ),
    );
  }
}
