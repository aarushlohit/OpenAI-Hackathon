import 'package:flutter/material.dart';

class CampaignPanel extends StatelessWidget {
  const CampaignPanel({required this.activeCampaigns, super.key});

  final int activeCampaigns;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            const Icon(Icons.hub, color: Color(0xFF22D3EE)),
            const SizedBox(width: 8),
            Text('Active Threat Campaigns: $activeCampaigns'),
          ],
        ),
      ),
    );
  }
}
