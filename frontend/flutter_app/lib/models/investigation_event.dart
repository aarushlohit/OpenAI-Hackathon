class InvestigationEvent {
  const InvestigationEvent({
    required this.event,
    required this.correlationId,
    required this.timestamp,
    required this.eventId,
    required this.payload,
    this.agent,
    this.eventVersion = '1.0',
    this.schemaHash = '',
    this.producer = 'hermes-x',
    this.trace = const {},
  });

  final String event;
  final String correlationId;
  final String timestamp;
  final String eventId;
  final String? agent;
  final Map<String, Object?> payload;
  final String eventVersion;
  final String schemaHash;
  final String producer;
  final Map<String, Object?> trace;

  factory InvestigationEvent.fromJson(Map<String, Object?> json) {
    final payload = json['payload'];
    return InvestigationEvent(
      event: json['event'] as String? ?? 'unknown',
      correlationId: json['correlation_id'] as String? ?? '',
      timestamp: json['timestamp'] as String? ?? '',
      eventId: json['event_id'] as String? ?? '',
      agent: json['agent'] as String?,
      payload: payload is Map<String, Object?> ? payload : const {},
      eventVersion: json['event_version'] as String? ?? '1.0',
      schemaHash: json['schema_hash'] as String? ?? '',
      producer: json['producer'] as String? ?? 'hermes-x',
      trace: json['trace'] is Map<String, Object?> ? json['trace'] as Map<String, Object?> : const {},
    );
  }
}
