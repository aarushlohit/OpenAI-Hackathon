import 'package:flutter/material.dart';

class SeverityMeter extends StatelessWidget {
  const SeverityMeter({required this.score, required this.label, super.key});

  final int score;
  final String label;

  @override
  Widget build(BuildContext context) {
    final normalized = score.clamp(0, 100) / 100;
    final color = score >= 85
        ? const Color(0xFFEF4444)
        : score >= 65
            ? const Color(0xFFF59E0B)
            : score > 0
                ? const Color(0xFF22D3EE)
                : const Color(0xFF10B981);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        LinearProgressIndicator(value: normalized, color: color, minHeight: 8),
      ],
    );
  }
}
