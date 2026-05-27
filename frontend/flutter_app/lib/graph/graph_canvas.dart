import 'package:flutter/material.dart';

import '../models/threat_graph.dart';

class GraphCanvas extends StatelessWidget {
  const GraphCanvas({required this.nodes, required this.edges, super.key});

  final List<ThreatGraphNode> nodes;
  final List<ThreatGraphEdge> edges;

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 350),
      child: CustomPaint(
        key: ValueKey('${nodes.length}:${edges.length}'),
        painter: _GraphPainter(nodes.length, edges.length),
        child: const SizedBox.expand(),
      ),
    );
  }
}

class _GraphPainter extends CustomPainter {
  const _GraphPainter(this.nodeCount, this.edgeCount);

  final int nodeCount;
  final int edgeCount;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = nodeCount > 3 ? const Color(0xFFFF4D6D) : const Color(0xFF00D1FF);
    final center = Offset(size.width / 2, size.height / 2);
    canvas.drawCircle(center, 16 + nodeCount.toDouble(), paint);
    if (edgeCount > 0) {
      final line = Paint()
        ..color = const Color(0xFF7CE3FF)
        ..strokeWidth = 1.5;
      canvas.drawLine(center.translate(-40, 0), center.translate(40, 0), line);
    }
  }

  @override
  bool shouldRepaint(covariant _GraphPainter oldDelegate) {
    return oldDelegate.nodeCount != nodeCount || oldDelegate.edgeCount != edgeCount;
  }
}
