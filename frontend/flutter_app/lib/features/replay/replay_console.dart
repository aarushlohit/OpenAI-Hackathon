import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../timeline/replay_controls.dart';
import '../investigation/investigation_controller.dart';

class ReplayConsole extends ConsumerStatefulWidget {
  const ReplayConsole({super.key});

  @override
  ConsumerState<ReplayConsole> createState() => _ReplayConsoleState();
}

class _ReplayConsoleState extends ConsumerState<ReplayConsole> {
  bool _playing = false;
  double _speed = 1.0;
  int _step = 0;

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(investigationControllerProvider);
    final eventCount = state.events.length;
    final cs = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(Icons.history, color: cs.primary, size: 16),
                const SizedBox(width: 8),
                const Expanded(child: Text('Replay Reconstruction')),
                if (state.replayVerified)
                  Icon(Icons.verified, size: 14, color: cs.tertiary)
                      .animate()
                      .fadeIn(duration: 400.ms),
                const SizedBox(width: 4),
                ReplayControls(
                  playing: _playing,
                  onPlayPause: () => setState(() {
                    _playing = !_playing;
                    if (_playing) _step = 0;
                  }),
                  onStep: () {
                    if (_step < eventCount - 1) setState(() => _step++);
                  },
                ),
              ],
            ),

            // Speed slider
            Row(
              children: [
                Icon(Icons.speed, size: 13, color: cs.onSurface.withValues(alpha: 0.5)),
                Expanded(
                  child: Slider(
                    value: _speed,
                    min: 0.25,
                    max: 4.0,
                    divisions: 15,
                    label: '${_speed.toStringAsFixed(2)}×',
                    onChanged: (v) => setState(() => _speed = v),
                  ),
                ),
              ],
            ),

            // Step indicator
            if (_playing && eventCount > 0)
              LinearProgressIndicator(
                value: eventCount > 0 ? _step / eventCount : 0,
                backgroundColor: cs.surfaceContainerHighest,
                color: cs.primary,
              ).animate().fadeIn(duration: 250.ms),

            const SizedBox(height: 4),

            // Status line
            Row(
              children: [
                Expanded(
                  child: Text(
                    '$eventCount replayable event(s)',
                    style: const TextStyle(fontSize: 11, color: Colors.white54),
                  ),
                ),
                if (state.replayVerified)
                  Text(
                    '✓ deterministic',
                    style: TextStyle(fontSize: 10, color: cs.tertiary),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
