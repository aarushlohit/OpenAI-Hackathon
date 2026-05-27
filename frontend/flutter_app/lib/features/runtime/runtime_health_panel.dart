import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../widgets/status_chip.dart';
import '../investigation/investigation_controller.dart';

final runtimeSummaryProvider = FutureProvider<Map<String, Object?>>((ref) async {
  final api = ref.watch(apiClientProvider);
  final health = await api.runtimeHealth();
  final bootstrap = await api.runtimeBootstrap();
  final metrics = await api.runtimeMetrics();
  final providers = await api.providerCapabilities();
  return {'health': health, 'bootstrap': bootstrap, 'metrics': metrics, 'providers': providers};
});

class RuntimeHealthPanel extends ConsumerWidget {
  const RuntimeHealthPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summary = ref.watch(runtimeSummaryProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: summary.when(
          loading: () => const LinearProgressIndicator(),
          error: (error, _) => Text('Runtime degraded: $error'),
          data: (data) {
            final health = data['health'] as Map<String, Object?>? ?? const {};
            final bootstrap = data['bootstrap'] as Map<String, Object?>? ?? const {};
            final metrics = data['metrics'] as Map<String, Object?>? ?? const {};
            return Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                StatusChip(label: 'Runtime', value: health['status']?.toString() ?? 'unknown'),
                StatusChip(label: 'Bootstrap', value: bootstrap['ready']?.toString() ?? 'unknown'),
                StatusChip(label: 'Redis publishes', value: metrics['redis_publishes']?.toString() ?? '0'),
                StatusChip(label: 'Replay', value: 'integrity online'),
                StatusChip(label: 'Graph rebuild', value: 'ready'),
              ],
            );
          },
        ),
      ),
    );
  }
}

