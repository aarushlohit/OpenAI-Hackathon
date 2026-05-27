import 'package:flutter/material.dart';

import '../models/investigation_event.dart';
import '../timeline/timeline_panel.dart';
import '../widgets/severity_meter.dart';
import '../widgets/status_chip.dart';
import 'campaign_panel.dart';
import 'provider_status_panel.dart';
import 'threat_feed_panel.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final List<InvestigationEvent> _events = const [];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('HERMES-X Terminal')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Expanded(
              flex: 2,
              child: Column(
                children: [
                  const SeverityMeter(score: 0, label: 'Awaiting Signal'),
                  const SizedBox(height: 12),
                  const CampaignPanel(activeCampaigns: 0),
                  const SizedBox(height: 12),
                  const ProviderStatusPanel(status: 'Standby'),
                  const SizedBox(height: 12),
                  const StatusChip(label: 'Provider Status', value: 'Standby'),
                  const SizedBox(height: 12),
                  Expanded(child: TimelinePanel(events: _events)),
                ],
              ),
            ),
            const SizedBox(width: 16),
            const Expanded(child: ThreatFeedPanel(items: ['Autonomous feed standby'])),
          ],
        ),
      ),
    );
  }
}
