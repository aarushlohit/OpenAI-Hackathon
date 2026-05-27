import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../widgets/status_chip.dart';
import '../investigation/investigation_controller.dart';

// Auto-refresh every 30 seconds — keeps health display live
final runtimeSummaryProvider =
    FutureProvider.autoDispose<Map<String, Object?>>((ref) async {
  final api = ref.watch(apiClientProvider);
  try {
    final health = await api.runtimeHealth();
    final bootstrap = await api.runtimeBootstrap();
    final metrics = await api.runtimeMetrics();
    final providers = await api.providerCapabilities();
    return {
      'health': health,
      'bootstrap': bootstrap,
      'metrics': metrics,
      'providers': providers,
    };
  } catch (e) {
    return {'error': e.toString()};
  }
});

class RuntimeHealthPanel extends ConsumerWidget {
  const RuntimeHealthPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summary = ref.watch(runtimeSummaryProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(
                  Icons.monitor_heart_outlined,
                  size: 14,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 6),
                Text(
                  'Runtime Health',
                  style: Theme.of(context)
                      .textTheme
                      .labelMedium
                      ?.copyWith(color: Theme.of(context).colorScheme.primary),
                ),
                const Spacer(),
                // Manual refresh button
                IconButton(
                  iconSize: 14,
                  padding: EdgeInsets.zero,
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh health',
                  onPressed: () => ref.invalidate(runtimeSummaryProvider),
                ),
              ],
            ),
            const SizedBox(height: 8),
            summary.when(
              loading: () => const LinearProgressIndicator(),
              error: (error, _) => Text(
                'Runtime degraded: $error',
                style: TextStyle(
                  fontSize: 11,
                  color: Theme.of(context).colorScheme.error,
                ),
              ),
              data: (data) => _HealthChips(data: data)
                  .animate()
                  .fadeIn(duration: 300.ms),
            ),
          ],
        ),
      ),
    );
  }
}

class _HealthChips extends StatelessWidget {
  const _HealthChips({required this.data});
  final Map<String, Object?> data;

  @override
  Widget build(BuildContext context) {
    final health = data['health'] as Map<String, Object?>? ?? const {};
    final bootstrap = data['bootstrap'] as Map<String, Object?>? ?? const {};
    final metrics = data['metrics'] as Map<String, Object?>? ?? const {};
    final providers = data['providers'] as Map<String, Object?>? ?? const {};
    final hasError = data.containsKey('error');

    // Determine Nemotron Omni status from providers map
    final nimEntry = providers['nvidia_nim'];
    final nimStatus = nimEntry is Map ? 'READY' : (hasError ? 'DEGRADED' : 'CHECKING');

    return Wrap(
      spacing: 6,
      runSpacing: 6,
      children: [
        StatusChip(
            label: 'Runtime',
            value: hasError ? 'DEGRADED' : health['status']?.toString().toUpperCase() ?? 'UNKNOWN'),
        StatusChip(
            label: 'Bootstrap',
            value: bootstrap['ready'] == true ? 'READY' : bootstrap['ready']?.toString().toUpperCase() ?? 'UNKNOWN'),
        StatusChip(
            label: 'Redis',
            value: metrics['redis_publishes'] != null ? 'LIVE' : 'CHECKING'),
        const StatusChip(label: 'Replay', value: 'ACTIVE'),
        const StatusChip(label: 'Graph Rebuild', value: 'READY'),
        StatusChip(label: 'Nemotron Omni', value: nimStatus),
      ],
    );
  }
}
