import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Beautiful verdict card — the primary result display.
class VerdictCard extends StatelessWidget {
  const VerdictCard({
    required this.score,
    required this.confidence,
    required this.severity,
    required this.summary,
    required this.provider,
    required this.failoverActive,
    super.key,
  });

  final int score;
  final double confidence;
  final String severity;
  final String summary;
  final String provider;
  final bool failoverActive;

  @override
  Widget build(BuildContext context) {
    final ColorScheme cs = Theme.of(context).colorScheme;
    final Color riskColor = _riskColor(severity);
    final String riskLabel = _riskLabel(severity);
    final String riskIcon = _riskEmoji(severity);
    final String confStr = confidence > 0
        ? '${(confidence * 100).toStringAsFixed(0)}%'
        : '${score.clamp(0, 100)}%';

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 640),
      child: Card(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(color: riskColor.withValues(alpha: 0.3), width: 1.5),
        ),
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              // ── Header: icon + risk label ─────────────────────────────
              Row(
                children: <Widget>[
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: riskColor.withValues(alpha: 0.12),
                    ),
                    child: Center(
                      child: Text(riskIcon, style: const TextStyle(fontSize: 22)),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(
                          riskLabel,
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                color: riskColor,
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        Text(
                          'Confidence: $confStr',
                          style: TextStyle(fontSize: 14, color: cs.onSurface.withValues(alpha: 0.55)),
                        ),
                      ],
                    ),
                  ),
                  // Score badge
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                    decoration: BoxDecoration(
                      color: riskColor.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(color: riskColor.withValues(alpha: 0.35)),
                    ),
                    child: Text(
                      '$score',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: riskColor,
                      ),
                    ),
                  ),
                ],
              ),

              // ── Score bar ─────────────────────────────────────────────
              const SizedBox(height: 20),
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: TweenAnimationBuilder<double>(
                  tween: Tween<double>(begin: 0, end: score.clamp(0, 100) / 100),
                  duration: const Duration(milliseconds: 800),
                  curve: Curves.easeOutCubic,
                  builder: (BuildContext ctx, double value, Widget? _) {
                    return LinearProgressIndicator(
                      value: value,
                      color: riskColor,
                      backgroundColor: riskColor.withValues(alpha: 0.10),
                      minHeight: 8,
                    );
                  },
                ),
              ),

              // ── Provider attribution ──────────────────────────────────
              const SizedBox(height: 16),
              _ProviderAttribution(
                provider: provider,
                failoverActive: failoverActive,
              ),

              // ── Action ────────────────────────────────────────────────
              const SizedBox(height: 16),
              Row(
                children: <Widget>[
                  Icon(Icons.info_outline, size: 14, color: cs.onSurface.withValues(alpha: 0.35)),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      _recommendation(severity),
                      style: TextStyle(
                        fontSize: 12,
                        color: cs.onSurface.withValues(alpha: 0.45),
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _riskColor(String risk) {
    switch (risk.toLowerCase()) {
      case 'critical': return const Color(0xFFDC2626);
      case 'high':     return const Color(0xFFF97316);
      case 'medium':   return const Color(0xFFF59E0B);
      default:         return const Color(0xFF10B981);
    }
  }

  String _riskLabel(String risk) {
    switch (risk.toLowerCase()) {
      case 'critical': return '🚨 Critical Threat Detected';
      case 'high':     return '⚠ High Risk Detected';
      case 'medium':   return 'Medium Risk Detected';
      default:         return 'Low Risk';
    }
  }

  String _riskEmoji(String risk) {
    switch (risk.toLowerCase()) {
      case 'critical': return '🚨';
      case 'high':     return '⚠️';
      case 'medium':   return '⚡';
      default:         return '✓';
    }
  }

  String _recommendation(String risk) {
    switch (risk.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'Do not engage. Preserve evidence and report to campus authorities.';
      case 'medium':
        return 'Exercise caution. Verify recruiter identity through official channels.';
      default:
        return 'Indicators suggest low risk, but remain vigilant.';
    }
  }
}

class _ProviderAttribution extends StatelessWidget {
  const _ProviderAttribution({required this.provider, required this.failoverActive});
  final String provider;
  final bool failoverActive;

  @override
  Widget build(BuildContext context) {
    final ColorScheme cs = Theme.of(context).colorScheme;
    final String providerLabel = _humanProvider(provider);

    return Row(
      children: <Widget>[
        Icon(Icons.memory, size: 12, color: cs.onSurface.withValues(alpha: 0.35)),
        const SizedBox(width: 6),
        Text(
          'Reasoned by: $providerLabel',
          style: TextStyle(fontSize: 11, color: cs.onSurface.withValues(alpha: 0.40)),
        ),
        if (failoverActive) ...<Widget>[
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: cs.secondary.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              'FAILOVER',
              style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: cs.secondary),
            ),
          ).animate(onPlay: (AnimationController c) => c.repeat(reverse: true))
              .fadeIn(duration: 700.ms),
        ],
      ],
    );
  }

  String _humanProvider(String p) {
    if (p.isEmpty) return 'OpenAI GPT-4.1 Mini';
    if (p.contains('nemotron') || p.contains('nvidia')) return 'NVIDIA Nemotron Omni';
    if (p.contains('openai')) return 'OpenAI GPT-4.1 Mini';
    if (p.contains('pollinations')) return 'Pollinations (Degraded)';
    return p;
  }
}
