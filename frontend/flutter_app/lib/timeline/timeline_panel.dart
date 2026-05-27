import 'package:flutter/material.dart';

import '../models/investigation_event.dart';
import 'timeline_entry.dart';

class TimelinePanel extends StatelessWidget {
  const TimelinePanel({required this.events, super.key});

  final List<InvestigationEvent> events;

  @override
  Widget build(BuildContext context) {
    final entries = events.map(TimelineEntry.fromEvent).toList();
    return ListView.separated(
      itemCount: entries.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final entry = entries[index];
        return ListTile(
          dense: true,
          title: Text(entry.title),
          subtitle: Text(
            entry.detail.isEmpty
                ? 'trace ${events[index].trace['trace_id'] ?? 'untracked'}'
                : '${entry.detail}\ntrace ${events[index].trace['trace_id'] ?? 'untracked'}',
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          trailing: Text(entry.timestamp.split('T').last),
        );
      },
    );
  }
}
