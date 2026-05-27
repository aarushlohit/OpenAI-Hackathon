import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../graph/graph_canvas.dart';
import '../../models/threat_graph.dart';
import '../investigation/investigation_controller.dart';

class ThreatGraphPanel extends ConsumerWidget {
  const ThreatGraphPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final events = ref.watch(investigationControllerProvider).events;
    final nodes = events
        .where((event) => event.event == 'graph_node_added')
        .map(
          (event) => ThreatGraphNode(
            id: event.payload['id']?.toString() ?? event.eventId,
            label: event.payload['label']?.toString() ?? 'entity',
            kind: event.payload['kind']?.toString() ?? 'unknown',
            severity: event.payload['severity']?.toString() ?? 'unknown',
          ),
        )
        .toList();
    final edges = events
        .where((event) => event.event == 'graph_edge_added')
        .map(
          (event) => ThreatGraphEdge(
            source: event.payload['source']?.toString() ?? '',
            target: event.payload['target']?.toString() ?? '',
            relation: event.payload['kind']?.toString() ?? 'linked_to',
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
