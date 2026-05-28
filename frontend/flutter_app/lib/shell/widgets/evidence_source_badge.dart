import 'package:flutter/material.dart';

/// Evidence source type — transparent attribution.
enum EvidenceSourceType {
  /// Signal derived from deterministic data (domain age, UPI reuse, TLS check).
  verified,

  /// Signal derived from AI model reasoning (behavior analysis, language patterns).
  aiReasoned,

  /// Signal combining deterministic data and AI reasoning (campaign correlation).
  hybrid,
}

/// Tiny colored badge showing evidence source type.
class EvidenceSourceBadge extends StatelessWidget {
  const EvidenceSourceBadge({required this.type, super.key});
  final EvidenceSourceType type;

  @override
  Widget build(BuildContext context) {
    final _BadgeConfig config = _config(type);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: config.color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: config.color.withValues(alpha: 0.35)),
      ),
      child: Text(
        config.label,
        style: TextStyle(
          fontSize: 9,
          fontWeight: FontWeight.bold,
          color: config.color,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  _BadgeConfig _config(EvidenceSourceType type) {
    switch (type) {
      case EvidenceSourceType.verified:
        return const _BadgeConfig(label: 'VERIFIED', color: Color(0xFF10B981));
      case EvidenceSourceType.aiReasoned:
        return const _BadgeConfig(label: 'AI', color: Color(0xFF60A5FA));
      case EvidenceSourceType.hybrid:
        return const _BadgeConfig(label: 'HYBRID', color: Color(0xFFF59E0B));
    }
  }
}

class _BadgeConfig {
  const _BadgeConfig({required this.label, required this.color});
  final String label;
  final Color color;
}
