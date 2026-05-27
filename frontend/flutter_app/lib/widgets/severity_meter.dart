import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Cinematic animated severity meter with pulse effect on high/critical.
class SeverityMeter extends StatelessWidget {
  const SeverityMeter({required this.score, required this.label, super.key});

  final int score;
  final String label;

  @override
  Widget build(BuildContext context) {
    final double normalized = score.clamp(0, 100) / 100;
    final Color barColor = _color(score);
    final bool isCritical = score >= 65;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Row(
              children: <Widget>[
                Icon(
                  isCritical ? Icons.gpp_bad : Icons.shield_outlined,
                  color: barColor,
                  size: 18,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    label.isEmpty ? 'AWAITING SIGNAL' : label,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: barColor,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.8,
                        ),
                  ),
                ),
                _ScoreBadge(score: score, color: barColor),
              ],
            ),
            const SizedBox(height: 10),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: TweenAnimationBuilder<double>(
                tween: Tween<double>(begin: 0, end: normalized),
                duration: const Duration(milliseconds: 600),
                curve: Curves.easeOutCubic,
                builder: (BuildContext ctx, double value, Widget? _) {
                  return LinearProgressIndicator(
                    value: value,
                    color: barColor,
                    backgroundColor:
                        barColor.withValues(alpha: 0.12),
                    minHeight: 10,
                  );
                },
              ),
            ),
            if (isCritical) ...<Widget>[
              const SizedBox(height: 6),
              _PulsingAlert(color: barColor, score: score)
                  .animate(onPlay: (AnimationController c) => c.repeat(reverse: true))
                  .fadeIn(duration: 700.ms),
            ],
          ],
        ),
      ),
    );
  }

  Color _color(int s) {
    if (s >= 85) return const Color(0xFFEF4444);
    if (s >= 65) return const Color(0xFFF97316);
    if (s >= 35) return const Color(0xFFF59E0B);
    if (s > 0) return const Color(0xFF22D3EE);
    return const Color(0xFF10B981);
  }
}

class _ScoreBadge extends StatelessWidget {
  const _ScoreBadge({required this.score, required this.color});
  final int score;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.45)),
      ),
      child: Text(
        '$score / 100',
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: color,
        ),
      ),
    );
  }
}

class _PulsingAlert extends StatelessWidget {
  const _PulsingAlert({required this.color, required this.score});
  final Color color;
  final int score;

  @override
  Widget build(BuildContext context) {
    final String label =
        score >= 85 ? '⚠ CRITICAL THREAT DETECTED' : '⚠ HIGH RISK SIGNAL';
    return Row(
      children: <Widget>[
        Icon(Icons.circle, size: 6, color: color),
        const SizedBox(width: 6),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: color,
            fontWeight: FontWeight.bold,
            letterSpacing: 0.9,
          ),
        ),
      ],
    );
  }
}
