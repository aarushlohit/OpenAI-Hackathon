import 'dart:async';
import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../core/api/hermes_api_client.dart';
import '../../core/websocket/investigation_socket.dart';
import '../../investigation/investigation_repository.dart';
import '../../models/chat_message.dart';
import '../../models/investigation_event.dart';

// ─── Providers ──────────────────────────────────────────────────────────────

final _uuid = const Uuid();

final chatApiClientProvider = Provider((ref) => HermesApiClient());
final chatSocketProvider =
    Provider((ref) => InvestigationSocket(Uri.parse('ws://localhost:8000')));
final chatRepositoryProvider = Provider(
  (ref) => InvestigationRepository(
    socket: ref.watch(chatSocketProvider),
    api: ref.watch(chatApiClientProvider),
  ),
);

final chatControllerProvider =
    StateNotifierProvider<ChatController, ChatControllerState>((ref) {
  return ChatController(ref.watch(chatRepositoryProvider));
});

// ── State ────────────────────────────────────────────────────────────────────

class ChatControllerState {
  const ChatControllerState({
    this.sessions = const [],
    this.activeSessionId = '',
    this.isComposing = false,
    this.pendingImageBytes,
    this.pendingImageName,
    this.pendingAudioName,
    this.pendingFiles = const [],
  });

  final List<ChatSession> sessions;
  final String activeSessionId;
  final bool isComposing;
  final Uint8List? pendingImageBytes;
  final String? pendingImageName;
  final String? pendingAudioName;
  final List<String> pendingFiles;

  ChatSession? get activeSession {
    if (activeSessionId.isEmpty) return null;
    try {
      return sessions.firstWhere((s) => s.id == activeSessionId);
    } catch (_) {
      return null;
    }
  }

  List<ChatMessage> get activeMessages =>
      activeSession?.messages ?? const [];

  ChatControllerState copyWith({
    List<ChatSession>? sessions,
    String? activeSessionId,
    bool? isComposing,
    Uint8List? pendingImageBytes,
    String? pendingImageName,
    String? pendingAudioName,
    List<String>? pendingFiles,
    bool clearPending = false,
  }) {
    return ChatControllerState(
      sessions: sessions ?? this.sessions,
      activeSessionId: activeSessionId ?? this.activeSessionId,
      isComposing: isComposing ?? this.isComposing,
      pendingImageBytes:
          clearPending ? null : pendingImageBytes ?? this.pendingImageBytes,
      pendingImageName:
          clearPending ? null : pendingImageName ?? this.pendingImageName,
      pendingAudioName:
          clearPending ? null : pendingAudioName ?? this.pendingAudioName,
      pendingFiles: clearPending ? const [] : pendingFiles ?? this.pendingFiles,
    );
  }
}

// ── Controller ───────────────────────────────────────────────────────────────

class ChatController extends StateNotifier<ChatControllerState> {
  ChatController(this._repository) : super(const ChatControllerState());

  final InvestigationRepository _repository;
  StreamSubscription<InvestigationEvent>? _subscription;

  // ── Session management ─────────────────────────────────────────────────

  void newSession() {
    state = state.copyWith(activeSessionId: '');
  }

  void selectSession(String sessionId) {
    state = state.copyWith(activeSessionId: sessionId);
  }

  // ── Pending attachments ────────────────────────────────────────────────

  void setPendingImage(Uint8List bytes, String name) {
    state = state.copyWith(pendingImageBytes: bytes, pendingImageName: name);
  }

  void setPendingAudio(String name) {
    state = state.copyWith(pendingAudioName: name);
  }

  void addPendingFile(String path) {
    state = state.copyWith(
      pendingFiles: [...state.pendingFiles, path],
    );
  }

  void clearPending() {
    state = state.copyWith(clearPending: true);
  }

  // ── Send message ───────────────────────────────────────────────────────

  Future<void> sendMessage(String text) async {
    if (text.isEmpty &&
        state.pendingImageBytes == null &&
        state.pendingAudioName == null) {
      return;
    }

    // Create or get session
    final sessionId =
        state.activeSessionId.isNotEmpty ? state.activeSessionId : _uuid.v4();

    // User message
    final userMsg = ChatMessage(
      id: _uuid.v4(),
      role: MessageRole.user,
      timestamp: DateTime.now(),
      text: text,
      imageBytes: state.pendingImageBytes,
      imageFileName: state.pendingImageName,
      audioFileName: state.pendingAudioName,
      uploadedFiles: List.from(state.pendingFiles),
    );

    // Hermes "thinking" placeholder
    final hermesId = _uuid.v4();
    final hermesMsg = ChatMessage(
      id: hermesId,
      role: MessageRole.hermes,
      timestamp: DateTime.now(),
      status: MessageStatus.investigating,
      investigationLogs: const ['Initializing investigation...'],
    );

    // Update state with both messages
    _upsertSession(sessionId, userMsg, hermesMsg);
    clearPending();

    // Start investigation
    try {
      String kind = 'text';
      String input = text;

      // If image pending, upload it first
      if (state.pendingImageBytes == null &&
          userMsg.imageBytes != null &&
          userMsg.imageFileName != null) {
        final uploadResult = await _repository.uploadFile(
          userMsg.imageFileName!,
          userMsg.imageFileName!,
        );
        input = uploadResult['file_reference']?.toString() ?? input;
        kind = 'image_reference';
      }

      final result = await _repository.start(input.isEmpty ? '(image analysis)' : input, kind: kind);
      final investigationId = result['investigation_id']?.toString() ?? '';
      final correlationId = result['correlation_id']?.toString() ?? '';
      final activeProvider = result['active_provider']?.toString() ?? '';
      final activeModel = result['active_model']?.toString() ?? '';
      final severity = _findingSeverity(result);
      final score = _scoreFromFinding(result);

      _updateHermesMsg(
        sessionId,
        hermesId,
        (m) => m.copyWith(
          status: score > 0 ? MessageStatus.done : MessageStatus.investigating,
          investigationId: investigationId,
          correlationId: correlationId,
          provider: _formatProvider(activeProvider, activeModel),
          severity: severity,
          threatScore: score,
        ),
      );

      // Subscribe to WebSocket events
      await _subscription?.cancel();
      _subscription = _repository.watch(correlationId).listen(
        (event) => _applyEvent(sessionId, hermesId, event),
        onError: (_) => _markDone(sessionId, hermesId),
        onDone: () => _markDone(sessionId, hermesId),
      );
    } catch (e) {
      _updateHermesMsg(
        sessionId,
        hermesId,
        (m) => m.copyWith(
          status: MessageStatus.error,
          text: 'Investigation failed: ${e.toString()}',
        ),
      );
    }
  }

  // ── Event reducer ──────────────────────────────────────────────────────

  void _applyEvent(String sessionId, String hermesId, InvestigationEvent event) {
    final payload = event.payload;

    final score = payload['score'] is int ? payload['score'] as int : null;
    final confidence = (payload['confidence'] as num?)?.toDouble();
    final severity = payload['severity']?.toString() ??
        payload['risk_level']?.toString();
    final provider = payload['provider']?.toString();
    final summaryRaw = payload['explainability_summary']?.toString();
    final breakdown = _extractBreakdown(payload);
    final replayVerified = event.event == 'replay_verified';
    final nodeInc = event.event == 'graph_node_added' ? 1 : 0;
    final edgeInc = event.event == 'graph_edge_added' ? 1 : 0;

    // Build log entry for streaming display
    String? logEntry;
    if (event.event == 'agent_progress' || event.event == 'investigation_progress') {
      logEntry = payload['message']?.toString();
    } else if (event.event == 'agent_started') {
      final agent = event.agent ?? 'agent';
      logEntry = '[${_agentLabel(agent)}] Starting...';
    } else if (event.event == 'agent_completed') {
      final agent = event.agent ?? 'agent';
      logEntry = '[${_agentLabel(agent)}] ✓ Complete';
    } else if (event.event == 'provider_failed') {
      logEntry = '⚠ Provider failover → ${payload['fallback_provider'] ?? 'backup'}';
    } else if (event.event == 'threat_detected') {
      logEntry = '🚨 Threat escalation triggered';
    } else if (event.event.startsWith('graph_')) {
      logEntry = '⬡ Graph: ${event.event.replaceAll('_', ' ')}';
    }

    _updateHermesMsg(sessionId, hermesId, (m) {
      final updatedLogs = logEntry != null
          ? [...m.investigationLogs, logEntry]
          : m.investigationLogs;
      final cappedLogs = updatedLogs.length > 100
          ? updatedLogs.sublist(updatedLogs.length - 100)
          : updatedLogs;

      final isDone = event.event == 'investigation_completed';

      return m.copyWith(
        status: isDone ? MessageStatus.done : MessageStatus.investigating,
        severity: severity ?? m.severity,
        threatScore: score ?? m.threatScore,
        confidence: confidence ?? m.confidence,
        provider: provider ?? m.provider,
        investigationLogs: cappedLogs,
        evidenceBreakdown: breakdown ?? m.evidenceBreakdown,
        explainabilitySummary: summaryRaw ?? m.explainabilitySummary,
        replayVerified: replayVerified ? true : m.replayVerified,
        graphNodeCount: m.graphNodeCount + nodeInc,
        graphEdgeCount: m.graphEdgeCount + edgeInc,
      );
    });
  }

  // ── Session helpers ────────────────────────────────────────────────────

  void _upsertSession(
    String sessionId,
    ChatMessage userMsg,
    ChatMessage hermesMsg,
  ) {
    final sessions = List<ChatSession>.from(state.sessions);
    final idx = sessions.indexWhere((s) => s.id == sessionId);

    if (idx == -1) {
      // New session
      final title = userMsg.text.isNotEmpty
          ? userMsg.text.substring(0, userMsg.text.length.clamp(0, 40))
          : userMsg.imageFileName ?? 'Investigation';
      sessions.insert(
        0,
        ChatSession(
          id: sessionId,
          title: title,
          createdAt: DateTime.now(),
          messages: [userMsg, hermesMsg],
        ),
      );
    } else {
      final session = sessions[idx];
      sessions[idx] = session.copyWith(
        messages: [...session.messages, userMsg, hermesMsg],
      );
    }

    state = state.copyWith(sessions: sessions, activeSessionId: sessionId);
  }

  void _updateHermesMsg(
    String sessionId,
    String hermesId,
    ChatMessage Function(ChatMessage) updater,
  ) {
    final sessions = List<ChatSession>.from(state.sessions);
    final idx = sessions.indexWhere((s) => s.id == sessionId);
    if (idx == -1) return;

    final session = sessions[idx];
    final messages = session.messages.map((m) {
      if (m.id == hermesId) return updater(m);
      return m;
    }).toList();

    // Update session severity
    final latestHermes = messages
        .where((m) => m.isHermes && m.severity != null)
        .lastOrNull;

    sessions[idx] = session.copyWith(
      messages: messages,
      severity: latestHermes?.severity,
    );
    state = state.copyWith(sessions: sessions);
  }

  void _markDone(String sessionId, String hermesId) {
    _updateHermesMsg(
      sessionId,
      hermesId,
      (m) => m.isInvestigating
          ? m.copyWith(status: MessageStatus.done)
          : m,
    );
  }

  // ── Formatting helpers ─────────────────────────────────────────────────

  String _formatProvider(String provider, String model) {
    if (provider.isEmpty) return 'OpenAI GPT-4.1 Mini';
    if (provider == 'nvidia_nim') return 'NVIDIA Nemotron Omni';
    if (provider == 'openai') return 'OpenAI GPT-4.1 Mini';
    if (provider == 'pollinations') return 'Pollinations Vision Runtime';
    return provider;
  }

  String _agentLabel(String agent) {
    const labels = {
      'behavior': 'BEHAVIOR',
      'behavior_analysis': 'BEHAVIOR',
      'osint': 'OSINT',
      'vision': 'VISION',
      'vision_analysis': 'VISION',
      'audio_analysis': 'AUDIO',
      'web_search': 'WEB VERIFY',
      'intake': 'INTAKE',
    };
    return labels[agent] ?? agent.toUpperCase();
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
    if (finding is Map) {
      final level = finding['risk_level']?.toString() ?? '';
      if (level == 'critical') return 95;
      if (level == 'high') return 80;
      if (level == 'medium') return 50;
      if (level == 'low') return 15;
    }
    return 0;
  }

  List<Map<String, Object?>>? _extractBreakdown(Map<String, Object?> payload) {
    final raw = payload['evidence_breakdown'];
    if (raw is! List) return null;
    return raw
        .whereType<Map<dynamic, dynamic>>()
        .map((m) => Map<String, Object?>.from(m))
        .toList();
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}
