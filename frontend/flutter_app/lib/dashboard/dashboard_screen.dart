import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../features/evidence/evidence_upload_panel.dart';
import '../features/evidence/explainability_panel.dart';
import '../features/graph/threat_graph_panel.dart';
import '../features/investigation/investigation_controller.dart';
import '../features/investigation/investigation_state.dart';
import '../models/investigation_event.dart';
import '../features/investigation/live_investigation_console.dart';
import '../features/replay/replay_console.dart';
import '../features/runtime/runtime_health_panel.dart';
import '../features/threat_feed/live_threat_feed_panel.dart';
import '../widgets/severity_meter.dart';
import 'campaign_panel.dart';
import 'provider_status_panel.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(investigationControllerProvider);
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const Text('HERMES-X Terminal'),
            const SizedBox(width: 16),
            if (state.failoverActive)
              _FailoverBadge(provider: state.activeProvider)
                  .animate(onPlay: (c) => c.repeat(reverse: true))
                  .fadeIn(duration: 600.ms),
            if (state.replayVerified)
              _ReplayVerifiedBadge()
                  .animate()
                  .fadeIn(duration: 400.ms),
          ],
        ),
        actions: [
          if (state.investigationId.isNotEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Chip(
                avatar: const Icon(Icons.fingerprint, size: 14),
                label: Text(
                  state.investigationId,
                  style: const TextStyle(fontSize: 10),
                ),
              ),
            ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            // ── Left column ──────────────────────────────────────────────
            Expanded(
              flex: 2,
              child: Column(
                children: [
                  SeverityMeter(score: state.threatScore, label: state.severity.toUpperCase()),
                  const SizedBox(height: 10),
                  CampaignPanel(activeCampaigns: _campaignSignals(state)),
                  const SizedBox(height: 10),
                  ProviderStatusPanel(status: state.status.name),
                  const SizedBox(height: 10),
                  const RuntimeHealthPanel(),
                  const SizedBox(height: 10),
                  const Expanded(child: LiveInvestigationConsole()),
                ],
              ),
            ),
            const SizedBox(width: 14),
            // ── Right column ─────────────────────────────────────────────
            const Expanded(
              child: Column(
                children: [
                  Expanded(flex: 3, child: ThreatGraphPanel()),
                  SizedBox(height: 10),
                  ReplayConsole(),
                  SizedBox(height: 10),
                  EvidenceUploadPanel(),
                  SizedBox(height: 10),
                  Expanded(flex: 2, child: ExplainabilityPanel()),
                  SizedBox(height: 10),
                  Expanded(child: LiveThreatFeedPanel()),
                ],
              ),
            ),
          ],
        ),
      ).animate().fadeIn(duration: 350.ms),
    );
  }

  int _campaignSignals(InvestigationState state) {
    return state.events
        .where((InvestigationEvent event) => event.event.contains('campaign'))
        .length;
  }
}

// ---------------------------------------------------------------------------
// Status badges
// ---------------------------------------------------------------------------

class _FailoverBadge extends StatelessWidget {
  const _FailoverBadge({required this.provider});
  final String provider;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.secondary.withValues(alpha: 0.18),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Theme.of(context).colorScheme.secondary.withValues(alpha: 0.55),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.swap_horiz, size: 12, color: Theme.of(context).colorScheme.secondary),
          const SizedBox(width: 4),
          Text(
            'FAILOVER → ${provider.isNotEmpty ? provider.toUpperCase() : "NEMOTRON"}',
            style: TextStyle(
              fontSize: 9,
              fontWeight: FontWeight.bold,
              color: Theme.of(context).colorScheme.secondary,
              letterSpacing: 0.8,
            ),
          ),
        ],
      ),
    );
  }
}

class _ReplayVerifiedBadge extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(left: 8),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.tertiary.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Theme.of(context).colorScheme.tertiary.withValues(alpha: 0.50),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.verified, size: 12, color: Theme.of(context).colorScheme.tertiary),
          const SizedBox(width: 4),
          Text(
            'REPLAY VERIFIED',
            style: TextStyle(
              fontSize: 9,
              fontWeight: FontWeight.bold,
              color: Theme.of(context).colorScheme.tertiary,
              letterSpacing: 0.8,
            ),
          ),
        ],
      ),
    );
  }
}
