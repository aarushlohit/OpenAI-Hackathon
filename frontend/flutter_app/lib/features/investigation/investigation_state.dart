import '../../models/investigation_event.dart';

enum SocketStatus { standby, connecting, live, degraded }

/// Extended investigation state — now carries explainability and provider failover info.
class InvestigationState {
  const InvestigationState({
    this.investigationId = '',
    this.correlationId = '',
    this.status = SocketStatus.standby,
    this.events = const [],
    this.threatScore = 0,
    this.confidence = 0.0,
    this.severity = 'awaiting signal',
    this.feed = const ['Autonomous feed standby'],
    this.error,
    this.activeProvider = '',
    this.failoverActive = false,
    this.explainabilitySummary = '',
    this.evidenceBreakdown = const [],
    this.replayVerified = false,
    this.graphNodeCount = 0,
    this.graphEdgeCount = 0,
  });

  final String investigationId;
  final String correlationId;
  final SocketStatus status;
  final List<InvestigationEvent> events;
  final int threatScore;
  final double confidence;
  final String severity;
  final List<String> feed;
  final String? error;

  // Provider failover
  final String activeProvider;
  final bool failoverActive;

  // Explainability
  final String explainabilitySummary;
  final List<Map<String, Object?>> evidenceBreakdown;

  // Replay
  final bool replayVerified;

  // Graph counters (denormalised for fast UI reads)
  final int graphNodeCount;
  final int graphEdgeCount;

  InvestigationState copyWith({
    String? investigationId,
    String? correlationId,
    SocketStatus? status,
    List<InvestigationEvent>? events,
    int? threatScore,
    double? confidence,
    String? severity,
    List<String>? feed,
    String? error,
    String? activeProvider,
    bool? failoverActive,
    String? explainabilitySummary,
    List<Map<String, Object?>>? evidenceBreakdown,
    bool? replayVerified,
    int? graphNodeCount,
    int? graphEdgeCount,
  }) {
    return InvestigationState(
      investigationId: investigationId ?? this.investigationId,
      correlationId: correlationId ?? this.correlationId,
      status: status ?? this.status,
      events: events ?? this.events,
      threatScore: threatScore ?? this.threatScore,
      confidence: confidence ?? this.confidence,
      severity: severity ?? this.severity,
      feed: feed ?? this.feed,
      error: error,
      activeProvider: activeProvider ?? this.activeProvider,
      failoverActive: failoverActive ?? this.failoverActive,
      explainabilitySummary: explainabilitySummary ?? this.explainabilitySummary,
      evidenceBreakdown: evidenceBreakdown ?? this.evidenceBreakdown,
      replayVerified: replayVerified ?? this.replayVerified,
      graphNodeCount: graphNodeCount ?? this.graphNodeCount,
      graphEdgeCount: graphEdgeCount ?? this.graphEdgeCount,
    );
  }
}
