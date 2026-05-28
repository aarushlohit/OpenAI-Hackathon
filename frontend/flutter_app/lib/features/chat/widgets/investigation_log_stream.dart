import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Streaming investigation log — shows live agent events as they arrive.
/// Looks like "⚡ [BEHAVIOR] Starting..." building up one by one.
class InvestigationLogStream extends StatelessWidget {
  const InvestigationLogStream({
    required this.logs,
    required this.isRunning,
    super.key,
  });

  final List<String> logs;
  final bool isRunning;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    if (logs.isEmpty && !isRunning) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: cs.onSurface.withValues(alpha: 0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              if (isRunning)
                SizedBox(
                  width: 12,
                  height: 12,
                  child: CircularProgressIndicator(
                    strokeWidth: 1.5,
                    color: cs.primary,
                  ),
                )
              else
                Icon(Icons.check_circle, size: 12, color: cs.primary),
              const SizedBox(width: 8),
              Text(
                isRunning ? '⚠ Investigation Running...' : 'Investigation Complete',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: isRunning ? cs.primary : cs.primary.withValues(alpha: 0.7),
                  letterSpacing: 0.3,
                ),
              ),
            ],
          ),

          if (logs.isNotEmpty) ...[
            const SizedBox(height: 10),
            ...logs.reversed.take(6).toList().reversed.map(
                  (log) => _LogLine(text: log),
                ),
            if (isRunning)
              _PulsingDots().animate(onPlay: (c) => c.repeat()),
          ],
        ],
      ),
    );
  }
}

class _LogLine extends StatelessWidget {
  const _LogLine({required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final isAgent = text.startsWith('[');
    final isDone = text.contains('✓');
    final isWarning = text.contains('⚠') || text.contains('failover');
    final isGraph = text.contains('⬡');

    Color textColor;
    if (isDone) {
      textColor = const Color(0xFF16A34A);
    } else if (isWarning) {
      textColor = const Color(0xFFF59E0B);
    } else if (isGraph) {
      textColor = const Color(0xFF7C3AED);
    } else {
      textColor = cs.onSurface.withValues(alpha: 0.55);
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 11,
          fontFamily: 'monospace',
          color: textColor,
          height: 1.4,
        ),
      ),
    ).animate().fadeIn(duration: 200.ms).slideX(begin: -0.02);
  }
}

class _PulsingDots extends StatefulWidget {
  @override
  State<_PulsingDots> createState() => _PulsingDotsState();
}

class _PulsingDotsState extends State<_PulsingDots>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat(reverse: true);
    _anim = Tween<double>(begin: 0.2, end: 1.0).animate(_ctrl);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: AnimatedBuilder(
        animation: _anim,
        builder: (context, _) => Row(
          children: List.generate(
            3,
            (i) => Container(
              width: 4,
              height: 4,
              margin: const EdgeInsets.only(right: 4),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: cs.primary.withValues(
                    alpha: ((i * 0.33 + _anim.value) % 1.0).clamp(0.1, 0.9)),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
