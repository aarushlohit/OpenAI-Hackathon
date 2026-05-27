import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../models/threat_graph.dart';

/// Animated graph canvas that renders threat nodes + edges with severity colour
/// coding and smooth entrance animations.  Works without the graphview package
/// so there are no runtime dependency issues.
class GraphCanvas extends StatefulWidget {
  const GraphCanvas({required this.nodes, required this.edges, super.key});

  final List<ThreatGraphNode> nodes;
  final List<ThreatGraphEdge> edges;

  @override
  State<GraphCanvas> createState() => _GraphCanvasState();
}

class _GraphCanvasState extends State<GraphCanvas>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulse;

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(vsync: this, duration: const Duration(seconds: 2))
      ..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.nodes.isEmpty) {
      return _EmptyGraphPlaceholder();
    }
    return AnimatedBuilder(
      animation: _pulse,
      builder: (ctx, _) => CustomPaint(
        painter: _GraphPainter(
          nodes: widget.nodes,
          edges: widget.edges,
          pulse: _pulse.value,
        ),
        child: const SizedBox.expand(),
      ),
    ).animate().fadeIn(duration: 350.ms);
  }
}

// ---------------------------------------------------------------------------
// Painter
// ---------------------------------------------------------------------------

class _GraphPainter extends CustomPainter {
  _GraphPainter({
    required this.nodes,
    required this.edges,
    required this.pulse,
  });

  final List<ThreatGraphNode> nodes;
  final List<ThreatGraphEdge> edges;
  final double pulse;

  @override
  void paint(Canvas canvas, Size size) {
    if (nodes.isEmpty) return;

    // --- compute node positions (radial layout) ---
    final positions = _layoutPositions(nodes, size);

    // --- draw edges ---
    final edgePaint = Paint()
      ..color = const Color(0xFF22D3EE).withValues(alpha: 0.28 + 0.12 * pulse)
      ..strokeWidth = 1.2
      ..style = PaintingStyle.stroke;
    final idxMap = {for (var i = 0; i < nodes.length; i++) nodes[i].id: i};
    for (final edge in edges) {
      final si = idxMap[edge.source];
      final ti = idxMap[edge.target];
      if (si == null || ti == null) continue;
      canvas.drawLine(positions[si], positions[ti], edgePaint);
    }

    // --- draw nodes ---
    for (var i = 0; i < nodes.length; i++) {
      _drawNode(canvas, nodes[i], positions[i]);
    }
  }

  List<Offset> _layoutPositions(List<ThreatGraphNode> nodes, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    if (nodes.length == 1) return [Offset(cx, cy)];
    final radius = math.min(cx, cy) * 0.65;
    final step = (2 * math.pi) / nodes.length;
    return List.generate(
      nodes.length,
      (i) => Offset(
        cx + radius * math.cos(step * i - math.pi / 2),
        cy + radius * math.sin(step * i - math.pi / 2),
      ),
    );
  }

  void _drawNode(Canvas canvas, ThreatGraphNode node, Offset pos) {
    final color = _nodeColor(node.severity);
    final r = node.kind == 'campaign' ? 18.0 : 13.0;

    // pulse ring for critical/high nodes
    if (node.severity == 'critical' || node.severity == 'high') {
      final ringPaint = Paint()
        ..color = color.withValues(alpha: 0.20 + 0.18 * pulse)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5;
      canvas.drawCircle(pos, r + 6 + 4 * pulse, ringPaint);
    }

    // node fill
    canvas.drawCircle(
      pos,
      r,
      Paint()..color = color.withValues(alpha: 0.80),
    );
    // node border
    canvas.drawCircle(
      pos,
      r,
      Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5,
    );

    // label
    final tp = TextPainter(
      text: TextSpan(
        text: node.label.length > 12 ? '${node.label.substring(0, 10)}…' : node.label,
        style: TextStyle(
          color: Colors.white.withValues(alpha: 0.90),
          fontSize: 9,
          fontWeight: FontWeight.w600,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout(maxWidth: 80);
    tp.paint(canvas, pos.translate(-tp.width / 2, r + 3));
  }

  Color _nodeColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return const Color(0xFFEF4444);
      case 'high':
        return const Color(0xFFF97316);
      case 'medium':
        return const Color(0xFFF59E0B);
      default:
        return const Color(0xFF22D3EE);
    }
  }

  @override
  bool shouldRepaint(covariant _GraphPainter old) =>
      old.pulse != pulse ||
      old.nodes.length != nodes.length ||
      old.edges.length != edges.length;
}

// ---------------------------------------------------------------------------
// Empty state
// ---------------------------------------------------------------------------

class _EmptyGraphPlaceholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.hub_outlined,
              size: 44, color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.35)),
          const SizedBox(height: 8),
          const Text(
            'Graph awaiting intelligence…',
            style: TextStyle(color: Colors.white30, fontSize: 12),
          ),
        ],
      ),
    );
  }
}
