import 'package:flutter/material.dart';
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
  double _speed = 1;

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(investigationControllerProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.history),
                const SizedBox(width: 8),
                const Expanded(child: Text('Replay Reconstruction')),
                ReplayControls(
                  playing: _playing,
                  onPlayPause: () => setState(() => _playing = !_playing),
                  onStep: () {},
                ),
              ],
            ),
            Slider(
              value: _speed,
              min: 0.25,
              max: 3,
              divisions: 11,
              label: '${_speed.toStringAsFixed(2)}x',
              onChanged: (value) => setState(() => _speed = value),
            ),
            Text('${state.events.length} replayable event(s) | snapshot validation ready'),
          ],
        ),
      ),
    );
  }
}

