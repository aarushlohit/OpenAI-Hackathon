import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/investigation_event.dart';
import '../investigation/investigation_controller.dart';
import '../investigation/investigation_state.dart';

/// Investigation Story Mode — renders a narrative timeline with step numbers,
/// human-readable event descriptions, and animated entrance per step.
class StoryTimelinePanel extends ConsumerWidget {
  const StoryTimelinePanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final InvestigationState state = ref.watch(investigationControllerProvider);
    final List<_StoryStep> steps = _buildStory(state);
    final ColorScheme cs = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.auto_stories, color: cs.primary, size: 16),
                const SizedBox(width: 8),
                Text(
                  'INVESTIGATION NARRATIVE',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        color: cs.primary,
                        letterSpacing: 1.2,
                      ),
                ),
                const Spacer(),
                Text(
                  '${steps.length} event(s)',
                  style: TextStyle(fontSize: 10, color: cs.onSurface.withValues(alpha: 0.4)),
                ),
              ],
            ),
            const Divider(height: 20),
            if (steps.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24),
                  child: Text(
                    'Awaiting cognition…',
                    style: TextStyle(color: cs.onSurface.withValues(alpha: 0.3), fontSize: 12),
                  ),
                ),
              )
            else
              Expanded(
                child: ListView.builder(
                  itemCount: steps.length,
                  itemBuilder: (BuildContext ctx, int i) {
                    final _StoryStep step = steps[i];
                    return _StoryStepTile(step: step, index: i)
                        .animate(delay: Duration(milliseconds: i * 80))
                        .fadeIn(duration: 300.ms)
                        .slideX(begin: -0.03);
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }

  List<_StoryStep> _buildStory(InvestigationState state) {
    final List<_StoryStep> steps = <_StoryStep>[];
    for (final InvestigationEvent event in state.events) {
      final _StoryStep? step = _eventToStep(event, state.severity);
      if (step != null) steps.add(step);
    }
    return steps;
  }

  _StoryStep? _eventToStep(InvestigationEvent event, String fallbackSeverity) {
    switch (event.event) {
      case 'investigation_started':
        return _StoryStep(
          icon: Icons.play_circle_outline,
          color: const Color(0xFF22D3EE),
          title: 'Investigation started',
          detail: 'Operator submitted evidence for autonomous analysis.',
          severity: 'info',
          timestamp: event.timestamp,
        );
      case 'agent_progress':
        final String agent = event.agent ?? 'Agent';
        final String message = event.payload['message']?.toString() ?? '';
        return _StoryStep(
          icon: Icons.psychology,
          color: const Color(0xFF8B5CF6),
          title: '${agent.replaceAll('_', ' ').toUpperCase()} reasoning',
          detail: message.isNotEmpty ? message : 'Agent analysing evidence.',
          severity: 'info',
          timestamp: event.timestamp,
        );
      case 'graph_node_added':
        final String label = event.payload['label']?.toString() ?? 'entity';
        final String kind = event.payload['kind']?.toString() ?? 'unknown';
        return _StoryStep(
          icon: Icons.account_tree,
          color: const Color(0xFF22D3EE),
          title: 'Graph entity detected: $label',
          detail: 'New $kind node added to threat intelligence graph.',
          severity: 'medium',
          timestamp: event.timestamp,
        );
      case 'graph_edge_added':
        final String relation = event.payload['kind']?.toString() ?? 'linked_to';
        final String source = event.payload['source']?.toString() ?? '';
        final String target = event.payload['target']?.toString() ?? '';
        return _StoryStep(
          icon: Icons.link,
          color: const Color(0xFFF59E0B),
          title: 'Relationship mapped: ${relation.replaceAll("_", " ")}',
          detail: '$source → $target',
          severity: 'medium',
          timestamp: event.timestamp,
        );
      case 'threat_escalated':
        final String reason = event.payload['reason']?.toString() ?? 'Multiple signals';
        return _StoryStep(
          icon: Icons.gpp_bad,
          color: const Color(0xFFEF4444),
          title: '🚨 Threat escalated',
          detail: reason,
          severity: 'high',
          timestamp: event.timestamp,
        );
      case 'provider_failed':
        final String fallback = event.payload['fallback_provider']?.toString() ?? 'nemotron';
        return _StoryStep(
          icon: Icons.swap_horiz,
          color: const Color(0xFFF59E0B),
          title: 'Provider failover activated',
          detail: 'Fallback cognition → $fallback (Nemotron Omni)',
          severity: 'warning',
          timestamp: event.timestamp,
        );
      case 'investigation_completed':
        final String risk = event.payload['risk_level']?.toString() ?? fallbackSeverity;
        final Object? score = event.payload['score'];
        return _StoryStep(
          icon: Icons.verified_user,
          color: _riskColor(risk),
          title: 'Investigation complete',
          detail: 'Verdict: ${risk.toUpperCase()} | Score: $score',
          severity: risk,
          timestamp: event.timestamp,
        );
      case 'replay_verified':
        return _StoryStep(
          icon: Icons.history_edu,
          color: const Color(0xFF10B981),
          title: 'Replay verified',
          detail: 'Deterministic reconstruction confirmed.',
          severity: 'info',
          timestamp: event.timestamp,
        );
      default:
        return null;
    }
  }

  Color _riskColor(String risk) {
    switch (risk.toLowerCase()) {
      case 'critical':
        return const Color(0xFFEF4444);
      case 'high':
        return const Color(0xFFF97316);
      case 'medium':
        return const Color(0xFFF59E0B);
      default:
        return const Color(0xFF10B981);
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────

class _StoryStep {
  const _StoryStep({
    required this.icon,
    required this.color,
    required this.title,
    required this.detail,
    required this.severity,
    required this.timestamp,
  });
  final IconData icon;
  final Color color;
  final String title;
  final String detail;
  final String severity;
  final String timestamp;
}

class _StoryStepTile extends StatelessWidget {
  const _StoryStepTile({required this.step, required this.index});
  final _StoryStep step;
  final int index;

  @override
  Widget build(BuildContext context) {
    final String timeStr = step.timestamp.contains('T')
        ? step.timestamp.split('T').last.split('.').first
        : step.timestamp;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Step number + icon
          Column(
            children: [
              Container(
                width: 26,
                height: 26,
                decoration: BoxDecoration(
                  color: step.color.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                  border: Border.all(color: step.color.withValues(alpha: 0.4)),
                ),
                child: Icon(step.icon, size: 13, color: step.color),
              ),
              if (index < 100)
                Container(
                  width: 1,
                  height: 16,
                  color: step.color.withValues(alpha: 0.20),
                ),
            ],
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        '${index + 1}. ${step.title}',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: step.color,
                        ),
                      ),
                    ),
                    Text(
                      timeStr,
                      style: const TextStyle(fontSize: 9, color: Colors.white30),
                    ),
                  ],
                ),
                if (step.detail.isNotEmpty)
                  Text(
                    step.detail,
                    style: const TextStyle(fontSize: 10, color: Colors.white54),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
