import 'dart:async';
import 'dart:collection';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../models/investigation_event.dart';

/// Hardened, fully typed WebSocket client.
///
/// Type safety guarantees:
/// - [seenIds] is [HashSet<String>] — no dynamic deduplication
/// - [controller] is [StreamController<InvestigationEvent>] — no dynamic stream
/// - All JSON payloads are cast via [InvestigationEvent.fromJson] before emission
/// - Reconnect uses typed callback signature
class InvestigationSocket {
  InvestigationSocket(
    this.baseUri, {
    this.maxBufferedEvents = 500,
    this.staleCutoffSeconds = 300,
  });

  final Uri baseUri;
  final int maxBufferedEvents;
  final int staleCutoffSeconds;

  Stream<InvestigationEvent> connect(String correlationId) {
    final StreamController<InvestigationEvent> controller =
        StreamController<InvestigationEvent>.broadcast();
    final Set<String> seenIds = HashSet<String>();
    var closed = false;
    var rendered = 0;

    Future<void> open([int attempt = 0]) async {
      if (closed) return;
      final Uri uri =
          baseUri.replace(path: '/v1/ws/investigations/$correlationId');
      WebSocketChannel? channel;
      try {
        channel = WebSocketChannel.connect(uri);
      } catch (_) {
        _scheduleReconnect(open, attempt);
        return;
      }

      channel.stream.listen(
        (Object? payload) {
          if (closed || payload is! String || rendered >= maxBufferedEvents) {
            return;
          }

          final Map<String, Object?> json;
          try {
            final Object? decoded = jsonDecode(payload);
            if (decoded is! Map<String, Object?>) return;
            json = decoded;
          } catch (_) {
            return; // malformed — skip silently
          }

          final InvestigationEvent event = InvestigationEvent.fromJson(json);

          // Deduplication guard
          if (event.eventId.isEmpty || seenIds.contains(event.eventId)) return;

          // Stale event protection
          if (_isStale(event.timestamp)) return;

          // Schema version guard
          if (event.eventVersion.isEmpty) return;

          seenIds.add(event.eventId);
          rendered += 1;
          controller.add(event);
        },
        onError: (_) => _scheduleReconnect(open, attempt),
        onDone: () {
          if (!closed) _scheduleReconnect(open, attempt);
        },
        cancelOnError: true,
      );
    }

    controller.onListen = () => open(0);
    controller.onCancel = () {
      closed = true;
    };
    return controller.stream;
  }

  void _scheduleReconnect(
    Future<void> Function([int attempt]) open,
    int attempt,
  ) {
    final int ms = (250 * (1 << attempt.clamp(0, 5))).clamp(250, 8000);
    Future<void>.delayed(Duration(milliseconds: ms), () => open(attempt + 1));
  }

  bool _isStale(String timestamp) {
    if (timestamp.isEmpty) return false;
    try {
      final DateTime ts = DateTime.parse(timestamp);
      final int age = DateTime.now().difference(ts).inSeconds.abs();
      return age > staleCutoffSeconds;
    } catch (_) {
      return false;
    }
  }
}
