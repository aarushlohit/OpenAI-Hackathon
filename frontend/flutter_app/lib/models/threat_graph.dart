class ThreatGraphNode {
  const ThreatGraphNode({
    required this.id,
    required this.label,
    required this.kind,
    this.severity = 'unknown',
  });

  final String id;
  final String label;
  final String kind;
  final String severity;

  factory ThreatGraphNode.fromJson(Map<String, Object?> json) {
    return ThreatGraphNode(
      id: json['id'] as String? ?? '',
      label: json['label'] as String? ?? '',
      kind: json['kind'] as String? ?? 'unknown',
      severity: json['severity'] as String? ?? 'unknown',
    );
  }
}

class ThreatGraphEdge {
  const ThreatGraphEdge({required this.source, required this.target, required this.relation});

  final String source;
  final String target;
  final String relation;

  factory ThreatGraphEdge.fromJson(Map<String, Object?> json) {
    return ThreatGraphEdge(
      source: json['source'] as String? ?? '',
      target: json['target'] as String? ?? '',
      relation: json['kind'] as String? ?? json['relation'] as String? ?? 'linked_to',
    );
  }
}

class ThreatGraphProjection {
  const ThreatGraphProjection({required this.nodes, required this.edges});

  final List<ThreatGraphNode> nodes;
  final List<ThreatGraphEdge> edges;
}
