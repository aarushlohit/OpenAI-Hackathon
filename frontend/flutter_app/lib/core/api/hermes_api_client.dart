import 'package:dio/dio.dart';

class HermesApiClient {
  HermesApiClient({Dio? dio, String baseUrl = 'http://localhost:8000'})
      : _dio = dio ?? Dio(BaseOptions(baseUrl: baseUrl, connectTimeout: const Duration(seconds: 5)));

  final Dio _dio;

  Future<Map<String, Object?>> startInvestigation({
    required String rawInput,
    String kind = 'text',
  }) async {
    final response = await _dio.post<Map<String, Object?>>(
      '/v1/investigate',
      data: {'raw_input': rawInput, 'kind': kind},
    );
    return response.data ?? const {};
  }

  Future<List<Map<String, Object?>>> investigationEvents(String investigationId) async {
    final response = await _dio.get<List<dynamic>>('/v1/investigations/$investigationId/events');
    return response.data
            ?.whereType<Map<dynamic, dynamic>>()
            .map((Map<dynamic, dynamic> item) => Map<String, Object?>.from(item))
            .toList() ??
        const [];
  }

  Future<Map<String, Object?>> replay(String investigationId) async {
    final response = await _dio.get<Map<String, Object?>>('/v1/investigations/$investigationId/replay');
    return response.data ?? const {};
  }

  Future<Map<String, Object?>> context(String investigationId) async {
    final response = await _dio.get<Map<String, Object?>>('/v1/investigations/$investigationId/context');
    return response.data ?? const {};
  }

  Future<Map<String, Object?>> runtimeHealth() async {
    final response = await _dio.get<Map<String, Object?>>('/v1/runtime/health');
    return response.data ?? const {};
  }

  Future<Map<String, Object?>> runtimeBootstrap() async {
    final response = await _dio.get<Map<String, Object?>>('/v1/runtime/bootstrap');
    return response.data ?? const {};
  }

  Future<Map<String, Object?>> runtimeMetrics() async {
    final response = await _dio.get<Map<String, Object?>>('/v1/observability/runtime-metrics');
    return response.data ?? const {};
  }

  Future<Map<String, Object?>> providerCapabilities() async {
    final response = await _dio.get<Map<String, Object?>>('/v1/providers/capabilities');
    return response.data ?? const {};
  }

  Future<List<String>> threatFeed() async {
    final response = await _dio.get<List<dynamic>>('/v1/threat-feed');
    return response.data
            ?.map((dynamic item) =>
                item is Map ? item['message'] ?? item['title'] ?? item.toString() : item.toString())
            .map((dynamic item) => item.toString())
            .toList() ??
        const [];
  }

  Future<Map<String, Object?>> lookup(String path) async {
    final response = await _dio.get<Map<String, Object?>>(path);
    return response.data ?? const {};
  }

  Future<Map<String, Object?>> uploadEvidence(String filePath, String fileName) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath, filename: fileName),
    });
    final response = await _dio.post<Map<String, Object?>>('/v1/investigate/upload', data: formData);
    return response.data ?? const {};
  }
}

