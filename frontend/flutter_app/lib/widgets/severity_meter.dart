import 'package:flutter/material.dart';

class SeverityMeter extends StatelessWidget {
  const SeverityMeter({required this.score, required this.label, super.key});

  final int score;
  final String label;

  @override
  Widget build(BuildContext context) {
    final normalized = score.clamp(0, 100) / 100;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        LinearProgressIndicator(value: normalized),
      ],
    );
  }
}

