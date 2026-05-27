import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/investigation_event.dart';
import '../investigation/investigation_controller.dart';
import '../investigation/investigation_state.dart';

/// Advanced Observability Panel — displays live throughput, provider latency,
/// failover count, active investigations, and replay/graph status.
class ObservabilityPanel extends ConsumerWidget {
  const ObservabilityPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final InvestigationState state = ref.watch(investigationControllerProvider);
    final ColorScheme cs = Theme.of(context).colorScheme;

    final int wsEvents = state.events.length;
    final int campaigns = state.events
        .where((InvestigationEvent e) => e.event.contains('campaign'))
        .length;
    final int graphNodes = state.graphNodeCount;
    final int graphEdges = state.graphEdgeCount;
    final int failoverCount = state.events
        .where((InvestigationEvent e) => e.event == 'provider_failed')
        .length;
    final String provider =
        state.activeProvider.isNotEmpty ? state.activeProvider : 'openai';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(Icons.analytics_outlined, color: cs.primary, size: 14),
                const SizedBox(width: 6),
                Text(
                  'LIVE OBSERVABILITY',
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: cs.primary,
                        letterSpacing: 1.2,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: <Widget>[
                _Metric(label: 'WS Events', value: '$wsEvents', icon: Icons.stream),
                _Metric(label: 'Graph Nodes', value: '$graphNodes', icon: Icons.hub),
                _Metric(label: 'Graph Edges', value: '$graphEdges', icon: Icons.timeline),
                _Metric(label: 'Campaigns', value: '$campaigns', icon: Icons.radar),
                _Metric(
                  label: 'Provider',
                  value: _shortProvider(provider),
                  icon: Icons.memory,
                  highlight: state.failoverActive,
                ),
                _Metric(
                  label: 'Failovers',
                  value: '$failoverCount',
                  icon: Icons.swap_horiz,
                  highlight: failoverCount > 0,
                ),
                _Metric(
                  label: 'Replay',
                  value: state.replayVerified ? 'VERIFIED' : 'PENDING',
                  icon: Icons.history_edu,
                  highlight: state.replayVerified,
                ),
              ],
            ),
          ],
        ),
      ),
    ).animate().fadeIn(duration: 350.ms);
  }

  String _shortProvider(String p) {
    if (p.contains('nemotron') || p.contains('nvidia')) return 'NEMOTRON';
    if (p.contains('openai')) return 'OPENAI';
    if (p.contains('pollinations')) return 'POLL.';
    return p.toUpperCase();
  }
}

class _Metric extends StatelessWidget {
  const _Metric({
    required this.label,
    required this.value,
    required this.icon,
    this.highlight = false,
  });
  final String label;
  final String value;
  final IconData icon;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    final Color base = highlight
        ? Theme.of(context).colorScheme.secondary
        : Theme.of(context).colorScheme.primary;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: base.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: base.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Icon(icon, size: 11, color: base),
          const SizedBox(width: 5),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text(
                value,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: base,
                ),
              ),
              Text(
                label,
                style: const TextStyle(fontSize: 9, color: Colors.white38),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
