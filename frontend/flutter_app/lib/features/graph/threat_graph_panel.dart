import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../graph/graph_canvas.dart';
import '../../models/investigation_event.dart';
import '../../models/threat_graph.dart';
import '../investigation/investigation_controller.dart';

class ThreatGraphPanel extends ConsumerWidget {
  const ThreatGraphPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final List<InvestigationEvent> events =
        ref.watch(investigationControllerProvider).events;

    final List<ThreatGraphNode> nodes = events
        .where((InvestigationEvent e) => e.event == 'graph_node_added')
        .map(
          (InvestigationEvent e) => ThreatGraphNode(
            id: e.payload['id']?.toString() ?? e.eventId,
            label: e.payload['label']?.toString() ?? 'entity',
            kind: e.payload['kind']?.toString() ?? 'unknown',
            severity: e.payload['severity']?.toString() ?? 'unknown',
          ),
        )
        .toList();

    final List<ThreatGraphEdge> edges = events
        .where((InvestigationEvent e) => e.event == 'graph_edge_added')
        .map(
          (InvestigationEvent e) => ThreatGraphEdge(
            source: e.payload['source']?.toString() ?? '',
            target: e.payload['target']?.toString() ?? '',
            relation: e.payload['kind']?.toString() ?? 'linked_to',
          ),
        )
        .toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(children: [Icon(Icons.hub), SizedBox(width: 8), Text('Threat Graph')]),
            const SizedBox(height: 8),
            Expanded(
              child: InteractiveViewer(
                minScale: 0.7,
                maxScale: 2.4,
                child: GraphCanvas(nodes: nodes, edges: edges),
              ),
            ),
            Text('${nodes.length} nodes | ${edges.length} edges | campaign overlay ready'),
          ],
        ),
      ),
    );
  }
}
