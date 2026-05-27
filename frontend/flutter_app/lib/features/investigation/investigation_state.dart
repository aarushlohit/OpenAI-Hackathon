import '../../models/investigation_event.dart';

enum SocketStatus { standby, connecting, live, degraded }

class InvestigationState {
  const InvestigationState({
    this.investigationId = '',
    this.correlationId = '',
    this.status = SocketStatus.standby,
    this.events = const [],
    this.threatScore = 0,
    this.severity = 'awaiting signal',
    this.feed = const ['Autonomous feed standby'],
    this.error,
  });

  final String investigationId;
  final String correlationId;
  final SocketStatus status;
  final List<InvestigationEvent> events;
  final int threatScore;
  final String severity;
  final List<String> feed;
  final String? error;

  InvestigationState copyWith({
    String? investigationId,
    String? correlationId,
    SocketStatus? status,
    List<InvestigationEvent>? events,
    int? threatScore,
    String? severity,
    List<String>? feed,
    String? error,
  }) {
    return InvestigationState(
      investigationId: investigationId ?? this.investigationId,
      correlationId: correlationId ?? this.correlationId,
      status: status ?? this.status,
      events: events ?? this.events,
      threatScore: threatScore ?? this.threatScore,
      severity: severity ?? this.severity,
      feed: feed ?? this.feed,
      error: error,
    );
  }
}

