/// Chat message model — represents one turn in the investigation conversation.
library;

import 'dart:typed_data';

enum MessageRole { user, hermes }

enum MessageStatus { pending, investigating, done, error }

/// A single message in the Hermes chat stream.
class ChatMessage {
  const ChatMessage({
    required this.id,
    required this.role,
    required this.timestamp,
    this.text = '',
    this.imageBytes,
    this.imageFileName,
    this.audioFileName,
    this.uploadedFiles = const [],
    this.status = MessageStatus.done,
    this.severity,
    this.threatScore,
    this.confidence,
    this.provider,
    this.failoverActive = false,
    this.investigationLogs = const [],
    this.evidenceBreakdown = const [],
    this.explainabilitySummary = '',
    this.investigationId = '',
    this.correlationId = '',
    this.replayVerified = false,
    this.graphNodeCount = 0,
    this.graphEdgeCount = 0,
  });

  final String id;
  final MessageRole role;
  final DateTime timestamp;
  final String text;

  // Attachments
  final Uint8List? imageBytes;
  final String? imageFileName;
  final String? audioFileName;
  final List<String> uploadedFiles;

  // Investigation state (only for hermes messages)
  final MessageStatus status;
  final String? severity;
  final int? threatScore;
  final double? confidence;
  final String? provider;
  final bool failoverActive;

  // Live streaming logs
  final List<String> investigationLogs;

  // Final evidence
  final List<Map<String, Object?>> evidenceBreakdown;
  final String explainabilitySummary;

  // Replay / graph
  final String investigationId;
  final String correlationId;
  final bool replayVerified;
  final int graphNodeCount;
  final int graphEdgeCount;

  bool get isUser => role == MessageRole.user;
  bool get isHermes => role == MessageRole.hermes;
  bool get isInvestigating => status == MessageStatus.investigating;
  bool get hasVerdict =>
      severity != null && severity != 'awaiting signal' && threatScore != null;

  ChatMessage copyWith({
    String? text,
    MessageStatus? status,
    String? severity,
    int? threatScore,
    double? confidence,
    String? provider,
    bool? failoverActive,
    List<String>? investigationLogs,
    List<Map<String, Object?>>? evidenceBreakdown,
    String? explainabilitySummary,
    String? investigationId,
    String? correlationId,
    bool? replayVerified,
    int? graphNodeCount,
    int? graphEdgeCount,
  }) {
    return ChatMessage(
      id: id,
      role: role,
      timestamp: timestamp,
      text: text ?? this.text,
      imageBytes: imageBytes,
      imageFileName: imageFileName,
      audioFileName: audioFileName,
      uploadedFiles: uploadedFiles,
      status: status ?? this.status,
      severity: severity ?? this.severity,
      threatScore: threatScore ?? this.threatScore,
      confidence: confidence ?? this.confidence,
      provider: provider ?? this.provider,
      failoverActive: failoverActive ?? this.failoverActive,
      investigationLogs: investigationLogs ?? this.investigationLogs,
      evidenceBreakdown: evidenceBreakdown ?? this.evidenceBreakdown,
      explainabilitySummary:
          explainabilitySummary ?? this.explainabilitySummary,
      investigationId: investigationId ?? this.investigationId,
      correlationId: correlationId ?? this.correlationId,
      replayVerified: replayVerified ?? this.replayVerified,
      graphNodeCount: graphNodeCount ?? this.graphNodeCount,
      graphEdgeCount: graphEdgeCount ?? this.graphEdgeCount,
    );
  }
}

/// Full chat session — list of messages and sidebar metadata.
class ChatSession {
  const ChatSession({
    required this.id,
    required this.title,
    required this.createdAt,
    this.messages = const [],
    this.severity,
  });

  final String id;
  final String title;
  final DateTime createdAt;
  final List<ChatMessage> messages;
  final String? severity; // highest severity in this session

  ChatSession copyWith({
    String? title,
    List<ChatMessage>? messages,
    String? severity,
  }) {
    return ChatSession(
      id: id,
      title: title ?? this.title,
      createdAt: createdAt,
      messages: messages ?? this.messages,
      severity: severity ?? this.severity,
    );
  }
}
