import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../../models/investigation_event.dart';

class InvestigationSocket {
  InvestigationSocket(this.baseUri, {this.maxBufferedEvents = 500});

  final Uri baseUri;
  final int maxBufferedEvents;

  Stream<InvestigationEvent> connect(String correlationId) {
    final controller = StreamController<InvestigationEvent>();
    var closed = false;

    Future<void> open([int attempt = 0]) async {
      if (closed) {
        return;
      }
      final uri = baseUri.replace(path: '/v1/ws/investigations/$correlationId');
      final channel = WebSocketChannel.connect(uri);
      var rendered = 0;
      channel.stream.listen(
        (payload) {
          if (payload is! String || rendered >= maxBufferedEvents) {
            return;
          }
          final json = jsonDecode(payload) as Map<String, Object?>;
          final event = InvestigationEvent.fromJson(json);
          if (event.eventVersion.isEmpty) {
            return;
          }
          rendered += 1;
          controller.add(event);
        },
        onError: (_) => _scheduleReconnect(open, attempt),
        onDone: () => _scheduleReconnect(open, attempt),
        cancelOnError: true,
      );
    }

    controller.onListen = open;
    controller.onCancel = () {
      closed = true;
    };
    return controller.stream;
  }

  void _scheduleReconnect(Future<void> Function([int attempt]) open, int attempt) {
    final delay = Duration(milliseconds: 250 * (attempt + 1).clamp(1, 8));
    Future<void>.delayed(delay, () => open(attempt + 1));
  }
}
