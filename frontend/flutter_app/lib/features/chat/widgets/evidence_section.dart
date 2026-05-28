import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Evidence breakdown section inside a Hermes message.
class EvidenceSection extends StatelessWidget {
  const EvidenceSection({required this.breakdown, super.key});
  final List<Map<String, Object?>> breakdown;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      margin: const EdgeInsets.only(top: 6),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: cs.onSurface.withValues(alpha: 0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.fact_check_outlined, size: 13, color: cs.primary),
              const SizedBox(width: 6),
              Text(
                'Evidence Signals',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: cs.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          for (int i = 0; i < breakdown.length; i++)
            _EvidenceRow(signal: breakdown[i], index: i),
        ],
      ),
    );
  }
}

class _EvidenceRow extends StatelessWidget {
  const _EvidenceRow({required this.signal, required this.index});
  final Map<String, Object?> signal;
  final int index;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final name = (signal['signal']?.toString() ?? 'unknown').replaceAll('_', ' ');
    final score = (signal['score_contribution'] as num?)?.toInt() ?? 0;
    final conf = (signal['confidence'] as num?)?.toDouble() ?? 0.0;
    final source = signal['source']?.toString() ?? 'agent';

    final color = _sourceColor(source);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(shape: BoxShape.circle, color: color),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              name,
              style: TextStyle(
                fontSize: 12,
                color: cs.onSurface.withValues(alpha: 0.8),
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Text(
            '+$score',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: cs.primary.withValues(alpha: 0.8),
            ),
          ),
          const SizedBox(width: 10),
          Text(
            '${(conf * 100).toStringAsFixed(0)}%',
            style: TextStyle(
              fontSize: 11,
              color: cs.onSurface.withValues(alpha: 0.4),
            ),
          ),
        ],
      ),
    ).animate(delay: Duration(milliseconds: index * 60)).fadeIn(duration: 200.ms);
  }

  Color _sourceColor(String source) {
    if (source.contains('deterministic')) return const Color(0xFF10B981);
    if (source.contains('consensus')) return const Color(0xFF7C3AED);
    if (source.contains('ai')) return const Color(0xFFD97706);
    return const Color(0xFF6B7280);
  }
}
