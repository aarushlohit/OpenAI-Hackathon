import 'package:animated_text_kit/animated_text_kit.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../timeline/replay_controls.dart';
import '../../timeline/timeline_panel.dart';
import '../../widgets/status_chip.dart';
import 'investigation_controller.dart';
import 'investigation_presets.dart';

class LiveInvestigationConsole extends ConsumerStatefulWidget {
  const LiveInvestigationConsole({super.key});

  @override
  ConsumerState<LiveInvestigationConsole> createState() => _LiveInvestigationConsoleState();
}

class _LiveInvestigationConsoleState extends ConsumerState<LiveInvestigationConsole> {
  final _controller = TextEditingController(
    text: 'Telegram HR from @careerfastjob claims direct internship selection. '
        'Asks refundable onboarding payment of 3500. Provides UPI pay@upi. '
        'Sends URL: https://career-fasttrack-placement.xyz. Claims limited slots.',
  );
  bool _playing = false;

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(investigationControllerProvider);
    final status = state.status.name.toUpperCase();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.terminal),
                const SizedBox(width: 8),
                Expanded(
                  child: AnimatedTextKit(
                    repeatForever: true,
                    pause: const Duration(seconds: 2),
                    animatedTexts: [TypewriterAnimatedText('HERMES-X LIVE INVESTIGATION CONSOLE')],
                  ),
                ),
                StatusChip(label: 'WebSocket', value: status),
              ],
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _controller,
              minLines: 2,
              maxLines: 4,
              decoration: const InputDecoration(border: OutlineInputBorder(), labelText: 'Evidence intake'),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                DropdownButton<InvestigationPreset>(
                  value: investigationPresets.firstWhere(
                    (InvestigationPreset preset) => preset.input == _controller.text,
                    orElse: () => investigationPresets.first,
                  ),
                  items: investigationPresets
                      .map((InvestigationPreset preset) =>
                          DropdownMenuItem<InvestigationPreset>(
                            value: preset,
                            child: Text(preset.name),
                          ))
                      .toList(),
                  onChanged: (preset) {
                    if (preset != null) {
                      setState(() => _controller.text = preset.input);
                    }
                  },
                ),
                const SizedBox(width: 8),
                FilledButton.icon(
                  onPressed: () => ref.read(investigationControllerProvider.notifier).start(_controller.text),
                  icon: const Icon(Icons.radar),
                  label: const Text('Run Investigation'),
                ),
                const SizedBox(width: 8),
                ReplayControls(
                  playing: _playing,
                  onPlayPause: () => setState(() => _playing = !_playing),
                  onStep: () {},
                ),
              ],
            ),
            const SizedBox(height: 10),
            if (state.investigationId.isNotEmpty)
              Text('Investigation ${state.investigationId} | Trace ${state.correlationId}'),
            const SizedBox(height: 10),
            Expanded(child: TimelinePanel(events: state.events)),
          ],
        ),
      ),
    );
  }
}
