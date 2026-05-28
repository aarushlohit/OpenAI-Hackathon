import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// The verdict banner inside a Hermes response — shows risk level, score, confidence.
/// Claude-style: clean, readable, minimal.
class VerdictBubble extends StatelessWidget {
  const VerdictBubble({
    required this.severity,
    required this.score,
    required this.confidence,
    required this.provider,
    required this.failoverActive,
    required this.replayVerified,
    super.key,
  });

  final String severity;
  final int score;
  final double confidence;
  final String provider;
  final bool failoverActive;
  final bool replayVerified;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final color = _riskColor(severity);
    final label = _riskLabel(severity);
    final rec = _recommendation(severity);
    final confStr = confidence > 0
        ? '${(confidence * 100).toStringAsFixed(0)}%'
        : '${score.clamp(0, 100)}%';

    return Container(
      margin: const EdgeInsets.only(top: 4, bottom: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.25), width: 1.5),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Risk header ─────────────────────────────────────────────
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: color.withValues(alpha: 0.12),
                  ),
                  child: Text(_riskEmoji(severity),
                      style: const TextStyle(fontSize: 18)),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        label,
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                          color: color,
                        ),
                      ),
                      Text(
                        'Confidence: $confStr',
                        style: TextStyle(
                          fontSize: 12,
                          color: cs.onSurface.withValues(alpha: 0.5),
                        ),
                      ),
                    ],
                  ),
                ),
                // Score badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: color.withValues(alpha: 0.3)),
                  ),
                  child: Text(
                    '$score',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                ),
              ],
            ),

            // ── Score bar ───────────────────────────────────────────────
            const SizedBox(height: 14),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: TweenAnimationBuilder<double>(
                tween: Tween<double>(begin: 0, end: score.clamp(0, 100) / 100),
                duration: const Duration(milliseconds: 900),
                curve: Curves.easeOutCubic,
                builder: (context, value, _) => LinearProgressIndicator(
                  value: value,
                  color: color,
                  backgroundColor: color.withValues(alpha: 0.10),
                  minHeight: 6,
                ),
              ),
            ),

            // ── Recommendation ──────────────────────────────────────────
            const SizedBox(height: 14),
            Text(
              'Recommended Action',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: cs.onSurface.withValues(alpha: 0.4),
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              rec,
              style: TextStyle(
                fontSize: 13,
                color: cs.onSurface.withValues(alpha: 0.75),
                height: 1.4,
              ),
            ),

            // ── Provider attribution ─────────────────────────────────────
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.memory, size: 11, color: cs.onSurface.withValues(alpha: 0.3)),
                const SizedBox(width: 5),
                Text(
                  'Primary Cognition: ${_humanProvider(provider)}',
                  style: TextStyle(
                    fontSize: 10,
                    color: cs.onSurface.withValues(alpha: 0.35),
                  ),
                ),
                if (failoverActive) ...[
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                    decoration: BoxDecoration(
                      color: Colors.orange.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text(
                      'FAILOVER',
                      style: TextStyle(fontSize: 8, color: Colors.orange, fontWeight: FontWeight.bold),
                    ),
                  ).animate(onPlay: (c) => c.repeat(reverse: true)).fadeIn(duration: 700.ms),
                ],
                if (replayVerified) ...[
                  const SizedBox(width: 8),
                  Icon(Icons.verified, size: 11, color: Colors.green.withValues(alpha: 0.7)),
                  const SizedBox(width: 3),
                  Text(
                    'Replay verified',
                    style: TextStyle(fontSize: 10, color: Colors.green.withValues(alpha: 0.6)),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _riskColor(String risk) {
    switch (risk.toLowerCase()) {
      case 'critical':
        return const Color(0xFFDC2626);
      case 'high':
        return const Color(0xFFF97316);
      case 'medium':
        return const Color(0xFFF59E0B);
      default:
        return const Color(0xFF16A34A);
    }
  }

  String _riskLabel(String risk) {
    switch (risk.toLowerCase()) {
      case 'critical':
        return '🚨 Critical Threat Detected';
      case 'high':
        return '⚠ High Risk Detected';
      case 'medium':
        return '⚡ Medium Risk Detected';
      default:
        return '✓ Low Risk — Appears Legitimate';
    }
  }

  String _riskEmoji(String risk) {
    switch (risk.toLowerCase()) {
      case 'critical':
        return '🚨';
      case 'high':
        return '⚠️';
      case 'medium':
        return '⚡';
      default:
        return '✓';
    }
  }

  String _recommendation(String risk) {
    switch (risk.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'Do not engage or send money. Preserve screenshots and report to campus authorities immediately.';
      case 'medium':
        return 'Exercise caution. Verify the recruiter\'s identity through official company channels before proceeding.';
      default:
        return 'Indicators suggest legitimate onboarding. Proceed normally but remain alert to unusual requests.';
    }
  }

  String _humanProvider(String p) {
    if (p.isEmpty) return 'OpenAI GPT-4.1 Mini';
    if (p.contains('nemotron') || p.contains('nvidia')) return 'NVIDIA Nemotron Omni';
    if (p.contains('openai')) return 'OpenAI GPT-4.1 Mini';
    if (p.contains('pollinations')) return 'Pollinations Vision Runtime';
    return p;
  }
}
