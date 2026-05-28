import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shell/hermes_app_shell.dart';
import '../../widgets/status_chip.dart';
import '../chat/chat_controller.dart';

/// MVP boot screen — boots runtime health, then transitions to DashboardScreen.
/// Shows a cinematic status banner while loading.
class MvpStatusScreen extends ConsumerWidget {
  const MvpStatusScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder<Map<String, Object?>>(
      future: _load(ref),
      builder: (context, snapshot) {
        final ready = snapshot.hasData && snapshot.error == null;
        final error = snapshot.error?.toString();
        return Scaffold(
          body: AnimatedSwitcher(
            duration: const Duration(milliseconds: 500),
            transitionBuilder: (child, animation) => FadeTransition(
              opacity: animation,
              child: child,
            ),
            child: ready
                ? const HermesAppShell()
                : _SplashScreen(
                    key: const ValueKey('splash'),
                    loading: !snapshot.hasError,
                    detail: error,
                  ),
          ),
        );
      },
    );
  }

  Future<Map<String, Object?>> _load(WidgetRef ref) async {
    final api = ref.read(chatApiClientProvider);
    try {
      final health = await api.runtimeHealth();
      final bootstrap = await api.runtimeBootstrap();
      final providers = await api.providerCapabilities();
      return {'health': health, 'bootstrap': bootstrap, 'providers': providers};
    } catch (_) {
      // Degrade gracefully — pass through to dashboard even if backend is cold
      return {'degraded': true};
    }
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen({required this.loading, this.detail, super.key});

  final bool loading;
  final String? detail;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 680),
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  children: [
                    Icon(Icons.security, color: cs.primary, size: 28),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'HERMES-X OPERATIONAL',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                color: cs.primary,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 1.5,
                              ),
                        ),
                        Text(
                          'Cyber Intelligence Runtime v1.0',
                          style: TextStyle(color: cs.onSurface.withValues(alpha: 0.45), fontSize: 12),
                        ),
                      ],
                    ),
                  ],
                ).animate().fadeIn(duration: 400.ms).slideY(begin: -0.05),

                const SizedBox(height: 24),

                // Progress
                if (loading)
                  LinearProgressIndicator(color: cs.primary, backgroundColor: cs.surfaceContainerHighest)
                      .animate(onPlay: (c) => c.repeat())
                      .shimmer(duration: 1200.ms, color: cs.primary.withValues(alpha: 0.6)),

                const SizedBox(height: 20),

                // Status chips
                const Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    StatusChip(label: 'Replay Engine', value: 'ACTIVE'),
                    StatusChip(label: 'Threat Graph', value: 'ACTIVE'),
                    StatusChip(label: 'Providers', value: 'CONNECTED'),
                    StatusChip(label: 'Runtime', value: 'HEALTHY'),
                    StatusChip(label: 'Nemotron Omni', value: 'READY'),
                  ],
                ).animate().fadeIn(delay: 200.ms, duration: 400.ms),

                const SizedBox(height: 20),

                // Doctrine lines
                const _DoctrineLine('Events define reality.'),
                const _DoctrineLine('Replay reconstructs cognition.'),
                const _DoctrineLine('Graphs project intelligence.'),
                const _DoctrineLine('Evidence drives escalation.'),

                if (detail != null) ...[
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: cs.error.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: cs.error.withValues(alpha: 0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.warning_amber, size: 14, color: cs.error),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            'Runtime warming: $detail',
                            style: TextStyle(fontSize: 11, color: cs.error),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _DoctrineLine extends StatelessWidget {
  const _DoctrineLine(this.text);
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Icon(Icons.chevron_right, size: 14,
              color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.55)),
          const SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(
              fontSize: 11,
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.50),
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 350.ms, duration: 300.ms);
  }
}
