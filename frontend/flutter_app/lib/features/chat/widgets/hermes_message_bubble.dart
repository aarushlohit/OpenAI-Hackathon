import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../models/chat_message.dart';
import 'investigation_log_stream.dart';
import 'verdict_bubble.dart';
import 'evidence_section.dart';

/// Hermes AI response bubble — contains streaming logs, verdict, evidence.
class HermesMessageBubble extends StatefulWidget {
  const HermesMessageBubble({required this.message, super.key});
  final ChatMessage message;

  @override
  State<HermesMessageBubble> createState() => _HermesMessageBubbleState();
}

class _HermesMessageBubbleState extends State<HermesMessageBubble> {
  bool _showTechnical = false;
  bool _showEvidence = true;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final msg = widget.message;

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 720),
        margin: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Hermes avatar + name ────────────────────────────────────
            Row(
              children: [
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: cs.primary.withValues(alpha: 0.15),
                    border: Border.all(color: cs.primary.withValues(alpha: 0.4)),
                  ),
                  child: Center(
                    child: Icon(Icons.shield, size: 14, color: cs.primary),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  'Hermes-X',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: cs.primary,
                    letterSpacing: 0.3,
                  ),
                ),
                if (msg.provider != null && msg.provider!.isNotEmpty) ...[
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                    decoration: BoxDecoration(
                      color: cs.onSurface.withValues(alpha: 0.07),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      msg.provider!,
                      style: TextStyle(
                        fontSize: 10,
                        color: cs.onSurface.withValues(alpha: 0.5),
                      ),
                    ),
                  ),
                ],
              ],
            ).animate().fadeIn(duration: 300.ms),

            const SizedBox(height: 12),

            // ── Streaming investigation log ──────────────────────────────
            if (msg.isInvestigating || msg.investigationLogs.isNotEmpty)
              InvestigationLogStream(
                logs: msg.investigationLogs,
                isRunning: msg.isInvestigating,
              ),

            // ── Verdict banner ───────────────────────────────────────────
            if (msg.hasVerdict)
              VerdictBubble(
                severity: msg.severity!,
                score: msg.threatScore ?? 0,
                confidence: msg.confidence ?? 0,
                provider: msg.provider ?? '',
                failoverActive: msg.failoverActive,
                replayVerified: msg.replayVerified,
              ).animate().fadeIn(duration: 400.ms).slideY(begin: 0.04),

            // ── Explainability story ─────────────────────────────────────
            if (msg.hasVerdict && msg.explainabilitySummary.isNotEmpty) ...[
              const SizedBox(height: 12),
              _ExplanationText(summary: msg.explainabilitySummary),
            ],

            // ── Evidence breakdown ───────────────────────────────────────
            if (msg.hasVerdict && msg.evidenceBreakdown.isNotEmpty) ...[
              const SizedBox(height: 8),
              GestureDetector(
                onTap: () => setState(() => _showEvidence = !_showEvidence),
                child: Row(
                  children: [
                    Icon(
                      _showEvidence
                          ? Icons.expand_less
                          : Icons.expand_more,
                      size: 16,
                      color: cs.onSurface.withValues(alpha: 0.4),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      _showEvidence
                          ? 'Hide evidence signals'
                          : 'Show evidence signals (${msg.evidenceBreakdown.length})',
                      style: TextStyle(
                        fontSize: 12,
                        color: cs.onSurface.withValues(alpha: 0.45),
                      ),
                    ),
                  ],
                ),
              ),
              if (_showEvidence)
                EvidenceSection(breakdown: msg.evidenceBreakdown)
                    .animate()
                    .fadeIn(duration: 250.ms),
            ],

            // ── Expandable technical details ─────────────────────────────
            if (msg.hasVerdict) ...[
              const SizedBox(height: 8),
              GestureDetector(
                onTap: () => setState(() => _showTechnical = !_showTechnical),
                child: Row(
                  children: [
                    Icon(
                      _showTechnical ? Icons.expand_less : Icons.expand_more,
                      size: 16,
                      color: cs.onSurface.withValues(alpha: 0.3),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      _showTechnical
                          ? 'Hide technical details'
                          : 'View technical analysis',
                      style: TextStyle(
                        fontSize: 12,
                        color: cs.onSurface.withValues(alpha: 0.35),
                      ),
                    ),
                  ],
                ),
              ),
              if (_showTechnical)
                _TechnicalDetailsPanel(message: msg)
                    .animate()
                    .fadeIn(duration: 250.ms),
            ],
          ],
        ),
      ),
    );
  }
}

// ── Explanation text ────────────────────────────────────────────────────────

class _ExplanationText extends StatelessWidget {
  const _ExplanationText({required this.summary});
  final String summary;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final lines = summary
        .split('\n')
        .where((s) => s.trim().isNotEmpty)
        .toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Why this was flagged:',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: cs.onSurface.withValues(alpha: 0.7),
          ),
        ),
        const SizedBox(height: 6),
        for (int i = 0; i < lines.length; i++)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('•',
                    style: TextStyle(color: cs.primary, fontSize: 14)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    lines[i].replaceFirst(RegExp(r'^[-•]\s*'), ''),
                    style: TextStyle(
                      fontSize: 14,
                      color: cs.onSurface.withValues(alpha: 0.85),
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          ).animate(delay: Duration(milliseconds: i * 80)).fadeIn(duration: 250.ms),
      ],
    );
  }
}

// ── Technical details panel ──────────────────────────────────────────────────

class _TechnicalDetailsPanel extends StatelessWidget {
  const _TechnicalDetailsPanel({required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: cs.surface.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: cs.onSurface.withValues(alpha: 0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _detailRow(context, 'Investigation ID', message.investigationId),
          _detailRow(context, 'Correlation ID', message.correlationId),
          _detailRow(context, 'Replay Verified', message.replayVerified ? 'Yes ✓' : 'Pending'),
          _detailRow(context, 'Graph Nodes', '${message.graphNodeCount}'),
          _detailRow(context, 'Graph Edges', '${message.graphEdgeCount}'),
          _detailRow(context, 'Primary Cognition', message.provider ?? 'Unknown'),
          if (message.investigationLogs.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              'Event Stream (last 10):',
              style: TextStyle(
                fontSize: 11,
                color: cs.onSurface.withValues(alpha: 0.5),
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 4),
            ...message.investigationLogs.reversed.take(10).map(
                  (log) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 1),
                    child: Text(
                      log,
                      style: TextStyle(
                        fontSize: 10,
                        fontFamily: 'monospace',
                        color: cs.onSurface.withValues(alpha: 0.4),
                      ),
                    ),
                  ),
                ),
          ],
        ],
      ),
    );
  }

  Widget _detailRow(BuildContext context, String label, String value) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text(
            '$label: ',
            style: TextStyle(
              fontSize: 11,
              color: cs.onSurface.withValues(alpha: 0.45),
              fontWeight: FontWeight.w500,
            ),
          ),
          Expanded(
            child: Text(
              value.isNotEmpty ? value : '—',
              style: TextStyle(
                fontSize: 11,
                color: cs.onSurface.withValues(alpha: 0.65),
                fontFamily: 'monospace',
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
