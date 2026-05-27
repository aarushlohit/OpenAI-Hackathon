import '../models/investigation_event.dart';

class TimelineEntry {
  const TimelineEntry({required this.title, required this.detail, required this.timestamp});

  final String title;
  final String detail;
  final String timestamp;

  factory TimelineEntry.fromEvent(InvestigationEvent event) {
    return TimelineEntry(
      title: event.agent ?? event.event,
      detail: event.payload['message']?.toString() ?? event.event,
      timestamp: event.timestamp,
    );
  }
}

