import 'package:flutter_test/flutter_test.dart';
import 'package:hermes_x/models/investigation_event.dart';

void main() {
  test('parses backend websocket event contract', () {
    final event = InvestigationEvent.fromJson({
      'event': 'agent_progress',
      'correlation_id': 'corr',
      'timestamp': '2026-05-27T00:00:00Z',
      'event_id': 'evt',
      'agent': 'behavior',
      'payload': {'message': 'ok'},
    });

    expect(event.event, 'agent_progress');
    expect(event.agent, 'behavior');
    expect(event.payload['message'], 'ok');
  });
}

