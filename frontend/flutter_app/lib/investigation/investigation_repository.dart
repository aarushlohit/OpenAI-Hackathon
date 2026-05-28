import '../core/api/hermes_api_client.dart';
import '../core/websocket/investigation_socket.dart';
import '../models/investigation_event.dart';

class InvestigationRepository {
  const InvestigationRepository({required this.socket, required this.api});

  final InvestigationSocket socket;
  final HermesApiClient api;

  Future<Map<String, Object?>> start(String input, {String kind = 'text'}) {
    return api.startInvestigation(rawInput: input, kind: kind);
  }

  Future<Map<String, Object?>> uploadFile(String filePath, String fileName) {
    return api.uploadEvidence(filePath, fileName);
  }

  Stream<InvestigationEvent> watch(String correlationId) {
    return socket.connect(correlationId);
  }

  Future<Map<String, Object?>> replay(String investigationId) => api.replay(investigationId);

  Future<List<Map<String, Object?>>> events(String investigationId) => api.investigationEvents(investigationId);
}
