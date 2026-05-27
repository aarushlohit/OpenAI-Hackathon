import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api/hermes_api_client.dart';
import '../../core/websocket/investigation_socket.dart';
import '../../investigation/investigation_repository.dart';
import '../../models/investigation_event.dart';
import 'investigation_state.dart';

final apiClientProvider = Provider((ref) => HermesApiClient());
final socketProvider =
    Provider((ref) => InvestigationSocket(Uri.parse('ws://localhost:8000')));
final investigationRepositoryProvider = Provider(
  (ref) => InvestigationRepository(
    socket: ref.watch(socketProvider),
    api: ref.watch(apiClientProvider),
  ),
);

final investigationControllerProvider =
    StateNotifierProvider<InvestigationController, InvestigationState>((ref) {
  return InvestigationController(ref.watch(investigationRepositoryProvider));
});

class InvestigationController extends StateNotifier<InvestigationState> {
  InvestigationController(this._repository) : super(const InvestigationState());

  final InvestigationRepository _repository;
  StreamSubscription<InvestigationEvent>? _subscription;

  // ── Public API ──────────────────────────────────────────────────────────

  Future<void> start(String input) async {
    state = state.copyWith(
      status: SocketStatus.connecting,
      events: const [],
      error: null,
      threatScore: 0,
      confidence: 0.0,
      severity: 'awaiting signal',
      explainabilitySummary: '',
      evidenceBreakdown: const [],
      failoverActive: false,
      replayVerified: false,
      graphNodeCount: 0,
      graphEdgeCount: 0,
    );

    final result = await _repository.start(input);
    final investigationId = result['investigation_id']?.toString() ?? '';
    final correlationId = result['correlation_id']?.toString() ?? '';

    state = state.copyWith(
      investigationId: investigationId,
      correlationId: correlationId,
      status: SocketStatus.live,
      severity: _findingSeverity(result),
      threatScore: _scoreFromFinding(result),
      activeProvider: result['provider']?.toString() ?? '',
    );

    await _subscription?.cancel();
    _subscription = _repository.watch(correlationId).listen(
      _applyEvent,
      onError: (_) => state = state.copyWith(status: SocketStatus.degraded),
      onDone: () => state = state.copyWith(status: SocketStatus.degraded),
    );
  }

  // ── Event reducer ───────────────────────────────────────────────────────

  void _applyEvent(InvestigationEvent event) {
    final payload = event.payload;

    // Bounded event list (newest 500)
    final events = [...state.events, event];
    final bounded = events.length > 500 ? events.sublist(events.length - 500) : events;

    // Score / severity
    final score = payload['score'] is int ? payload['score'] as int : state.threatScore;
    final confidence = (payload['confidence'] as num?)?.toDouble() ?? state.confidence;
    final severity = payload['severity']?.toString() ??
        payload['risk_level']?.toString() ??
        state.severity;

    // Provider failover
    final provider = payload['provider']?.toString() ?? state.activeProvider;
    final failover = event.event == 'provider_failed' ? true : state.failoverActive;

    // Explainability
    final summary = payload['explainability_summary']?.toString() ?? state.explainabilitySummary;
    final breakdown = _extractBreakdown(payload) ?? state.evidenceBreakdown;

    // Graph counters
    final nodeCount = event.event == 'graph_node_added'
        ? state.graphNodeCount + 1
        : state.graphNodeCount;
    final edgeCount = event.event == 'graph_edge_added'
        ? state.graphEdgeCount + 1
        : state.graphEdgeCount;

    // Replay verification
    final replayVerified = event.event == 'replay_verified' ? true : state.replayVerified;

    // Threat feed entry
    final feedEntry = _feedFor(event);

    state = state.copyWith(
      status: SocketStatus.live,
      events: bounded,
      threatScore: score,
      confidence: confidence,
      severity: severity,
      activeProvider: provider,
      failoverActive: failover,
      explainabilitySummary: summary,
      evidenceBreakdown: breakdown,
      graphNodeCount: nodeCount,
      graphEdgeCount: edgeCount,
      replayVerified: replayVerified,
      feed: feedEntry == null
          ? state.feed
          : [feedEntry, ...state.feed].take(24).toList(),
    );
  }

  // ── Helpers ─────────────────────────────────────────────────────────────

  String _findingSeverity(Map<String, Object?> result) {
    final finding = result['finding'];
    if (finding is Map && finding['risk_level'] != null) {
      return finding['risk_level'].toString();
    }
    return 'awaiting signal';
  }

  int _scoreFromFinding(Map<String, Object?> result) {
    final finding = result['finding'];
    if (finding is Map) {
      final level = finding['risk_level']?.toString() ?? '';
      if (level == 'critical') return 95;
      if (level == 'high') return 80;
      if (level == 'medium') return 50;
    }
    return 0;
  }

  List<Map<String, Object?>>? _extractBreakdown(Map<String, Object?> payload) {
    final raw = payload['evidence_breakdown'];
    if (raw is! List) return null;
    return raw
        .whereType<Map>()
        .map((m) => Map<String, Object?>.from(m))
        .toList();
  }

  String? _feedFor(InvestigationEvent event) {
    switch (event.event) {
      case 'agent_progress':
        return '${event.agent ?? "agent"}: ${event.payload["message"] ?? "progress"}';
      case 'provider_failed':
        return '⚠ Provider failover → ${event.payload["fallback_provider"] ?? "nemotron"}';
      case 'threat_escalated':
        return '🚨 Threat escalated: ${event.payload["reason"] ?? event.event}';
      case 'replay_verified':
        return '✓ Replay verified — deterministic reconstruction confirmed';
      default:
        if (event.event.startsWith('graph_')) {
          return 'Graph: ${event.event.replaceAll("_", " ")} detected';
        }
        if (event.event.contains('threat') || event.event.contains('campaign')) {
          return 'Intel: ${event.event.replaceAll("_", " ")}';
        }
        return null;
    }
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}
