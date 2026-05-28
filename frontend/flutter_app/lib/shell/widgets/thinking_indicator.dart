import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../models/investigation_event.dart';

/// Animated thinking indicator — shows human-readable reasoning stages.
class ThinkingIndicator extends StatelessWidget {
  const ThinkingIndicator({required this.events, super.key});
  final List<InvestigationEvent> events;

  @override
  Widget build(BuildContext context) {
    final ColorScheme cs = Theme.of(context).colorScheme;
    final List<String> stages = _stagesFromEvents(events);
    final String current = stages.isNotEmpty ? stages.last : 'Starting investigation…';

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 520),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: <Widget>[
              // Animated pulsing icon
              _PulsingIcon(color: cs.primary)
                  .animate(onPlay: (AnimationController c) => c.repeat(reverse: true))
                  .scale(begin: const Offset(0.92, 0.92), end: const Offset(1.08, 1.08), duration: 1200.ms),

              const SizedBox(height: 20),

              // Current stage
              Text(
                current,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: cs.onSurface.withValues(alpha: 0.80),
                    ),
              ).animate().fadeIn(duration: 300.ms),

              const SizedBox(height: 16),

              // Progress dots
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  for (int i = 0; i < 3; i++)
                    Container(
                      margin: const EdgeInsets.symmetric(horizontal: 3),
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: cs.primary.withValues(alpha: 0.5),
                      ),
                    ).animate(
                      onPlay: (AnimationController c) => c.repeat(reverse: true),
                      delay: Duration(milliseconds: i * 200),
                    ).fadeIn(duration: 600.ms),
                ],
              ),

              const SizedBox(height: 16),

              // History of stages
              if (stages.length > 1)
                Column(
                  children: <Widget>[
                    for (int i = 0; i < stages.length - 1; i++)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: <Widget>[
                            Icon(Icons.check_circle, size: 12, color: cs.tertiary),
                            const SizedBox(width: 6),
                            Flexible(
                              child: Text(
                                stages[i],
                                style: TextStyle(fontSize: 12, color: cs.onSurface.withValues(alpha: 0.45)),
                              ),
                            ),
                          ],
                        ),
                      ).animate(delay: Duration(milliseconds: i * 60)).fadeIn(duration: 200.ms),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }

  List<String> _stagesFromEvents(List<InvestigationEvent> events) {
    final List<String> stages = <String>[];
    for (final InvestigationEvent event in events) {
      final String? stage = _mapEventToStage(event);
      if (stage != null && !stages.contains(stage)) stages.add(stage);
    }
    if (stages.isEmpty) stages.add('Starting investigation…');
    return stages;
  }

  String? _mapEventToStage(InvestigationEvent event) {
    switch (event.event) {
      case 'investigation_started':
        return 'Analyzing submitted evidence…';
      case 'agent_progress':
        final String agent = event.agent?.replaceAll('_', ' ') ?? 'agent';
        final String message = event.payload['message']?.toString() ?? '';
        if (message.isNotEmpty) return message;
        if (agent.contains('behavior')) return 'Analyzing recruiter behavior…';
        if (agent.contains('osint')) return 'Checking domain intelligence…';
        if (agent.contains('vision')) return 'Processing visual evidence…';
        return 'Agent reasoning: $agent';
      case 'graph_node_added':
        return 'Reconstructing threat graph…';
      case 'graph_edge_added':
        return 'Correlating scam campaign signals…';
      case 'threat_escalated':
        return 'Evaluating threat escalation…';
      case 'provider_failed':
        return 'Switching cognition provider…';
      default:
        return null;
    }
  }
}

class _PulsingIcon extends StatelessWidget {
  const _PulsingIcon({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color.withValues(alpha: 0.12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Icon(Icons.psychology, color: color, size: 24),
    );
  }
}
