import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../investigation/investigation_controller.dart';
import '../investigation/investigation_state.dart';

/// Cinematic live threat feed with event-driven animation.
class LiveThreatFeedPanel extends ConsumerWidget {
  const LiveThreatFeedPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final InvestigationState state = ref.watch(investigationControllerProvider);
    final List<String> feed = state.feed;
    final ColorScheme cs = Theme.of(context).colorScheme;

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 10, 12, 4),
            child: Row(
              children: <Widget>[
                Icon(Icons.warning_amber, color: cs.secondary, size: 14),
                const SizedBox(width: 6),
                Text(
                  'THREAT FEED',
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: cs.secondary,
                        letterSpacing: 1.2,
                      ),
                ),
                const Spacer(),
                Container(
                  width: 6,
                  height: 6,
                  decoration: BoxDecoration(
                    color: state.status == SocketStatus.live
                        ? cs.tertiary
                        : cs.error,
                    shape: BoxShape.circle,
                  ),
                ).animate(onPlay: (AnimationController c) => c.repeat(reverse: true))
                    .fadeIn(duration: 800.ms),
                const SizedBox(width: 4),
                Text(
                  state.status.name.toUpperCase(),
                  style: TextStyle(fontSize: 9, color: cs.onSurface.withValues(alpha: 0.4)),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: feed.isEmpty
                ? Center(
                    child: Text(
                      'Feed monitoring…',
                      style: TextStyle(
                        color: cs.onSurface.withValues(alpha: 0.3),
                        fontSize: 11,
                      ),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    itemCount: feed.length,
                    itemBuilder: (BuildContext ctx, int i) {
                      return _FeedEntry(text: feed[i], index: i)
                          .animate(delay: Duration(milliseconds: i == 0 ? 0 : 40))
                          .fadeIn(duration: 250.ms);
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _FeedEntry extends StatelessWidget {
  const _FeedEntry({required this.text, required this.index});
  final String text;
  final int index;

  @override
  Widget build(BuildContext context) {
    final bool isAlert = text.startsWith('🚨') || text.startsWith('⚠');
    final bool isProvider = text.startsWith('⚠ Provider') || text.contains('failover');
    final bool isVerified = text.startsWith('✓');
    final Color iconColor = isAlert
        ? Theme.of(context).colorScheme.error
        : isProvider
            ? Theme.of(context).colorScheme.secondary
            : isVerified
                ? Theme.of(context).colorScheme.tertiary
                : Theme.of(context).colorScheme.primary;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Icon(
            isAlert ? Icons.gpp_bad : isVerified ? Icons.check_circle : Icons.chevron_right,
            size: 12,
            color: iconColor,
          ),
          const SizedBox(width: 6),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 11,
                color: index == 0
                    ? iconColor
                    : Colors.white60,
                fontWeight: index == 0 ? FontWeight.w600 : FontWeight.normal,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
