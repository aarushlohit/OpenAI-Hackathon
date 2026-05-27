import 'package:flutter/material.dart';

class ReplayControls extends StatelessWidget {
  const ReplayControls({
    required this.playing,
    required this.onPlayPause,
    required this.onStep,
    super.key,
  });

  final bool playing;
  final VoidCallback onPlayPause;
  final VoidCallback onStep;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        IconButton(
          tooltip: playing ? 'Pause replay' : 'Play replay',
          icon: Icon(playing ? Icons.pause : Icons.play_arrow),
          onPressed: onPlayPause,
        ),
        IconButton(
          tooltip: 'Step event',
          icon: const Icon(Icons.skip_next),
          onPressed: onStep,
        ),
      ],
    );
  }
}
