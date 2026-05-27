import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../investigation/investigation_controller.dart';

class LiveThreatFeedPanel extends ConsumerWidget {
  const LiveThreatFeedPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final feed = ref.watch(investigationControllerProvider).feed;
    return Card(
      child: ListView.separated(
        padding: const EdgeInsets.all(8),
        itemCount: feed.length,
        separatorBuilder: (_, __) => const Divider(height: 1),
        itemBuilder: (context, index) => ListTile(
          dense: true,
          leading: const Icon(Icons.warning_amber),
          title: Text(feed[index]),
        ),
      ),
    );
  }
}

