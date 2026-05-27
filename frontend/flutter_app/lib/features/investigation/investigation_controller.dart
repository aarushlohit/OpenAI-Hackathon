import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api/hermes_api_client.dart';
import '../../core/websocket/investigation_socket.dart';
import '../../investigation/investigation_repository.dart';
import '../../models/investigation_event.dart';
import 'investigation_state.dart';

final apiClientProvider = Provider((ref) => HermesApiClient());
final socketProvider = Provider((ref) => InvestigationSocket(Uri.parse('ws://localhost:8000')));
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

  Future<void> start(String input) async {
    state = state.copyWith(status: SocketStatus.connecting, events: const [], error: null);
    final result = await _repository.start(input);
    final investigationId = result['investigation_id']?.toString() ?? '';
    final correlationId = result['correlation_id']?.toString() ?? '';
    state = state.copyWith(
      investigationId: investigationId,
      correlationId: correlationId,
      status: SocketStatus.live,
      severity: _findingSeverity(result),
      threatScore: _scoreFromFinding(result),
    );
    await _subscription?.cancel();
    _subscription = _repository.watch(correlationId).listen(
      _applyEvent,
      onError: (_) => state = state.copyWith(status: SocketStatus.degraded),
      onDone: () => state = state.copyWith(status: SocketStatus.degraded),
    );
  }

  void _applyEvent(InvestigationEvent event) {
    final events = [...state.events, event];
    final payload = event.payload;
    final score = payload['score'] is int ? payload['score'] as int : state.threatScore;
    final severity = payload['severity']?.toString() ?? payload['risk_level']?.toString() ?? state.severity;
    final feed = _feedFor(event);
    state = state.copyWith(
      status: SocketStatus.live,
      events: events.length > 500 ? events.sublist(events.length - 500) : events,
      threatScore: score,
      severity: severity,
      feed: feed == null ? state.feed : [feed, ...state.feed].take(24).toList(),
    );
  }

  String _findingSeverity(Map<String, Object?> result) {
    final finding = result['finding'];
    if (finding is Map && finding['risk_level'] != null) {
      return finding['risk_level'].toString();
    }
    return 'awaiting signal';
  }

  int _scoreFromFinding(Map<String, Object?> result) {
    final finding = result['finding'];
    if (finding is Map && finding['risk_level'] == 'high') {
      return 80;
    }
    if (finding is Map && finding['risk_level'] == 'critical') {
      return 95;
    }
    return 0;
  }

  String? _feedFor(InvestigationEvent event) {
    if (event.event == 'agent_progress') {
      return '${event.agent ?? 'agent'}: ${event.payload['message'] ?? 'progress'}';
    }
    if (event.event.startsWith('graph_')) {
      return 'Graph intelligence: ${event.event}';
    }
    if (event.event.contains('threat') || event.event.contains('campaign')) {
      return 'Threat feed: ${event.event}';
    }
    return null;
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}

