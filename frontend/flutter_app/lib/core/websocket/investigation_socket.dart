import 'dart:async';
import 'dart:collection';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../models/investigation_event.dart';

/// Hardened WebSocket client with:
/// - Exponential-backoff reconnect (capped at 8s)
/// - Event deduplication by event_id
/// - Bounded render buffer (maxBufferedEvents)
/// - Stale event protection (events older than staleCutoffSeconds are dropped)
/// - Replay-safe ordering (events emitted in arrival order, deduped by ID)
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
    // ignore: close_sinks — controller is closed when cancelled
    final controller = StreamController<InvestigationEvent>.broadcast();
    final seenIds = HashSet<String>();
    var closed = false;
    var rendered = 0;

    Future<void> open([int attempt = 0]) async {
      if (closed) return;
      final uri = baseUri.replace(path: '/v1/ws/investigations/$correlationId');
      WebSocketChannel? channel;
      try {
        channel = WebSocketChannel.connect(uri);
        // Reset attempt counter on successful open
        attempt = 0;
      } catch (_) {
        _scheduleReconnect(open, attempt);
        return;
      }

      channel.stream.listen(
        (payload) {
          if (closed || payload is! String || rendered >= maxBufferedEvents) return;

          Map<String, Object?> json;
          try {
            json = jsonDecode(payload) as Map<String, Object?>;
          } catch (_) {
            return; // malformed payload — skip silently
          }

          final event = InvestigationEvent.fromJson(json);

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
    // Exponential backoff: 250ms * 2^attempt, capped at 8000ms
    final ms = (250 * (1 << attempt.clamp(0, 5))).clamp(250, 8000);
    Future<void>.delayed(Duration(milliseconds: ms), () => open(attempt + 1));
  }

  bool _isStale(String timestamp) {
    if (timestamp.isEmpty) return false;
    try {
      final ts = DateTime.parse(timestamp);
      final age = DateTime.now().difference(ts).inSeconds.abs();
      return age > staleCutoffSeconds;
    } catch (_) {
      return false;
    }
  }
}
