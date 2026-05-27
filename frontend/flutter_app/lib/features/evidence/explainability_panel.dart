import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../investigation/investigation_controller.dart';
import '../investigation/investigation_state.dart';

/// Explainability panel — shows WHY a threat verdict was reached.
/// Driven by payload fields injected into InvestigationState from events.
class ExplainabilityPanel extends ConsumerWidget {
  const ExplainabilityPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(investigationControllerProvider);
    final cs = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.psychology_alt, color: cs.primary, size: 18),
                const SizedBox(width: 8),
                Text(
                  'WHY THIS WAS FLAGGED',
                  style: Theme.of(context)
                      .textTheme
                      .labelLarge
                      ?.copyWith(color: cs.primary, letterSpacing: 1.2),
                ),
                const Spacer(),
                _ConfidenceBadge(confidence: _confidence(state)),
              ],
            ),
            const Divider(height: 20),
            _VerdictBanner(state: state),
            const SizedBox(height: 12),
            Expanded(child: _SignalList(state: state)),
          ],
        ),
      ),
    ).animate().fadeIn(duration: 400.ms).slideY(begin: 0.06);
  }

  double _confidence(InvestigationState state) {
    // Extract aggregate confidence from most recent score event
    for (final event in state.events.reversed) {
      final c = event.payload['confidence'];
      if (c is num) return c.toDouble().clamp(0.0, 1.0);
    }
    return 0.0;
  }
}

class _VerdictBanner extends StatelessWidget {
  const _VerdictBanner({required this.state});
  final InvestigationState state;

  @override
  Widget build(BuildContext context) {
    final severity = state.severity.toUpperCase();
    final color = _severityColor(state.severity, context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Row(
        children: [
          Icon(_severityIcon(state.severity), color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'VERDICT: $severity  |  Score: ${state.threatScore}/100',
              style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  Color _severityColor(String s, BuildContext ctx) {
    final cs = Theme.of(ctx).colorScheme;
    switch (s.toLowerCase()) {
      case 'critical':
        return cs.error;
      case 'high':
        return const Color(0xFFEF4444);
      case 'medium':
        return cs.secondary;
      default:
        return cs.tertiary;
    }
  }

  IconData _severityIcon(String s) {
    switch (s.toLowerCase()) {
      case 'critical':
      case 'high':
        return Icons.gpp_bad;
      case 'medium':
        return Icons.warning_amber;
      default:
        return Icons.check_circle_outline;
    }
  }
}

class _SignalList extends StatelessWidget {
  const _SignalList({required this.state});
  final InvestigationState state;

  @override
  Widget build(BuildContext context) {
    final signals = _extractSignals(state);
    if (signals.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.radar, size: 40, color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.4)),
            const SizedBox(height: 8),
            const Text('Awaiting evidence signals…', style: TextStyle(color: Colors.white38)),
          ],
        ),
      );
    }
    return ListView.builder(
      itemCount: signals.length,
      itemBuilder: (ctx, i) => _SignalTile(signal: signals[i])
          .animate(delay: Duration(milliseconds: i * 60))
          .fadeIn(duration: 280.ms)
          .slideX(begin: -0.04),
    );
  }

  List<_Signal> _extractSignals(InvestigationState state) {
    final out = <_Signal>[];
    // Pull from evidence_breakdown in any scoring event payload
    for (final event in state.events) {
      final breakdown = event.payload['evidence_breakdown'];
      if (breakdown is List) {
        for (final item in breakdown) {
          if (item is Map) {
            out.add(_Signal(
              signal: item['signal']?.toString() ?? 'unknown',
              confidence: (item['confidence'] as num?)?.toDouble() ?? 0,
              contribution: (item['score_contribution'] as num?)?.toInt() ?? 0,
              source: item['source']?.toString() ?? 'agent',
              detail: item['detail']?.toString() ?? '',
            ));
          }
        }
      }
    }
    // Deduplicate by signal key, keep highest contribution
    final deduped = <String, _Signal>{};
    for (final s in out) {
      if (!deduped.containsKey(s.signal) ||
          (deduped[s.signal]!.contribution < s.contribution)) {
        deduped[s.signal] = s;
      }
    }
    return deduped.values.toList()
      ..sort((a, b) => b.contribution.compareTo(a.contribution));
  }
}

class _SignalTile extends StatelessWidget {
  const _SignalTile({required this.signal});
  final _Signal signal;

  @override
  Widget build(BuildContext context) {
    final pct = (signal.confidence * 100).toStringAsFixed(0);
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(Icons.circle, size: 8, color: _signalColor(signal.confidence, cs)),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  signal.signal.replaceAll('_', ' ').toUpperCase(),
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, letterSpacing: 0.6),
                ),
                if (signal.detail.isNotEmpty)
                  Text(signal.detail, style: const TextStyle(fontSize: 10, color: Colors.white54)),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('+${signal.contribution}pts',
                  style: TextStyle(fontSize: 11, color: cs.primary, fontWeight: FontWeight.bold)),
              Text('$pct% conf',
                  style: const TextStyle(fontSize: 10, color: Colors.white38)),
            ],
          ),
        ],
      ),
    );
  }

  Color _signalColor(double conf, ColorScheme cs) {
    if (conf >= 0.85) return cs.error;
    if (conf >= 0.65) return cs.secondary;
    return cs.tertiary;
  }
}

class _ConfidenceBadge extends StatelessWidget {
  const _ConfidenceBadge({required this.confidence});
  final double confidence;

  @override
  Widget build(BuildContext context) {
    final pct = (confidence * 100).toStringAsFixed(1);
    final color = confidence >= 0.75
        ? const Color(0xFFEF4444)
        : confidence >= 0.50
            ? Theme.of(context).colorScheme.secondary
            : Theme.of(context).colorScheme.tertiary;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Text(
        '$pct% confidence',
        style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.bold),
      ),
    );
  }
}

class _Signal {
  const _Signal({
    required this.signal,
    required this.confidence,
    required this.contribution,
    required this.source,
    required this.detail,
  });
  final String signal;
  final double confidence;
  final int contribution;
  final String source;
  final String detail;
}
