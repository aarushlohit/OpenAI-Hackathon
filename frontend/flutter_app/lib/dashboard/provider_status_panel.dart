import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Polished provider status panel showing active provider, failover state,
/// and WebSocket connection status.
class ProviderStatusPanel extends StatelessWidget {
  const ProviderStatusPanel({
    required this.status,
    required this.provider,
    required this.failoverActive,
    super.key,
  });

  final String status;
  final String provider;
  final bool failoverActive;

  @override
  Widget build(BuildContext context) {
    final ColorScheme cs = Theme.of(context).colorScheme;
    final Color statusColor = failoverActive ? cs.secondary : cs.tertiary;
    final String providerLabel = _providerLabel(provider);
    final String statusLabel = failoverActive ? 'FAILOVER ACTIVE' : status.toUpperCase();

    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(
          children: <Widget>[
            Icon(Icons.dns, color: statusColor, size: 16),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text(
                    providerLabel,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: statusColor,
                    ),
                  ),
                  Text(
                    statusLabel,
                    style: const TextStyle(fontSize: 10, color: Colors.white38),
                  ),
                ],
              ),
            ),
            if (failoverActive)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: cs.secondary.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  'NEMOTRON OMNI',
                  style: TextStyle(
                    fontSize: 9,
                    fontWeight: FontWeight.bold,
                    color: cs.secondary,
                  ),
                ),
              ).animate(onPlay: (AnimationController c) => c.repeat(reverse: true))
                  .fadeIn(duration: 700.ms),
          ],
        ),
      ),
    );
  }

  String _providerLabel(String p) {
    if (p.isEmpty) return 'Provider Infrastructure';
    if (p.contains('nemotron') || p.contains('nvidia')) {
      return 'Nemotron Omni (NVIDIA NIM)';
    }
    if (p.contains('openai')) return 'OpenAI (Primary)';
    if (p.contains('pollinations')) return 'Pollinations (Degraded Fallback)';
    return p;
  }
}
