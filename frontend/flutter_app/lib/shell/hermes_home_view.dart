import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';

import '../features/investigation/investigation_controller.dart';
import '../features/investigation/investigation_state.dart';
import 'widgets/evidence_source_badge.dart';
import 'widgets/suggestion_pill.dart';
import 'widgets/thinking_indicator.dart';
import 'widgets/verdict_card.dart';

/// Human-first home view — Claude-style conversational experience.
class HermesHomeView extends ConsumerStatefulWidget {
  const HermesHomeView({super.key});

  @override
  ConsumerState<HermesHomeView> createState() => _HermesHomeViewState();
}

class _HermesHomeViewState extends ConsumerState<HermesHomeView> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final InvestigationState state = ref.watch(investigationControllerProvider);
    final ColorScheme cs = Theme.of(context).colorScheme;
    final bool isInvestigating = state.status == SocketStatus.connecting || state.status == SocketStatus.live;
    final bool hasVerdict = state.threatScore > 0 && state.severity != 'awaiting signal';

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 24),
      child: Column(
        children: <Widget>[
          // ── Top: Brand ───────────────────────────────────────────────
          if (!isInvestigating && !hasVerdict) ...<Widget>[
            const SizedBox(height: 60),
            Icon(Icons.shield_outlined, size: 40, color: cs.primary)
                .animate()
                .fadeIn(duration: 500.ms)
                .scale(begin: const Offset(0.8, 0.8)),
            const SizedBox(height: 14),
            Text(
              'Hermes-X',
              style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                    color: cs.primary,
                    fontWeight: FontWeight.bold,
                  ),
            ).animate().fadeIn(delay: 100.ms, duration: 400.ms),
            const SizedBox(height: 6),
            Text(
              'Protecting students from recruitment scams.',
              style: Theme.of(context).textTheme.bodyMedium,
            ).animate().fadeIn(delay: 200.ms, duration: 400.ms),
            const SizedBox(height: 48),
          ],

          // ── Center: Results area (scrollable) ────────────────────────
          Expanded(
            child: SingleChildScrollView(
              controller: _scrollController,
              child: Column(
                children: <Widget>[
                  // Thinking animation
                  if (isInvestigating && !hasVerdict)
                    ThinkingIndicator(events: state.events)
                        .animate()
                        .fadeIn(duration: 350.ms),

                  // Verdict card
                  if (hasVerdict) ...<Widget>[
                    VerdictCard(
                      score: state.threatScore,
                      confidence: state.confidence,
                      severity: state.severity,
                      summary: state.explainabilitySummary,
                      provider: state.activeProvider,
                      failoverActive: state.failoverActive,
                    ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.05),
                    const SizedBox(height: 20),

                    // Explainability story
                    if (state.explainabilitySummary.isNotEmpty)
                      _ExplainabilityStory(summary: state.explainabilitySummary)
                          .animate(delay: 200.ms)
                          .fadeIn(duration: 400.ms),

                    // Evidence breakdown
                    if (state.evidenceBreakdown.isNotEmpty) ...<Widget>[
                      const SizedBox(height: 16),
                      _EvidenceBreakdownList(breakdown: state.evidenceBreakdown)
                          .animate(delay: 300.ms)
                          .fadeIn(duration: 400.ms),
                    ],
                  ],
                ],
              ),
            ),
          ),

          // ── Bottom: Input area ──────────────────────────────────────
          const SizedBox(height: 16),

          // Suggestion pills (only before first investigation)
          if (!isInvestigating && !hasVerdict)
            Wrap(
              spacing: 8,
              runSpacing: 8,
              alignment: WrapAlignment.center,
              children: <Widget>[
                SuggestionPill(label: 'Analyze Telegram Recruiter', onTap: () => _fill('Telegram HR from @careerfastjob claims direct internship selection. Asks refundable onboarding payment of 3500. Provides UPI pay@upi. Sends URL: https://career-fasttrack-placement.xyz. Claims limited slots.')),
                SuggestionPill(label: 'Verify Internship Website', onTap: () => _fill('Verify internship onboarding at https://new-careers.xyz/verify. Recruiter claims direct selection and Telegram-only communication.')),
                SuggestionPill(label: 'Check Offer Letter', onTap: () => _fill('Offer letter requires refundable security deposit before joining and bypasses interview. HR from hr@infosys-careers-rpo.xyz.')),
                SuggestionPill(label: 'Investigate LinkedIn Recruiter', onTap: () => _fill('Recruiter using hr@career-fasttrack-placement.xyz asks for documents and sends Telegram handle @careerfastjob for onboarding payment.')),
              ],
            ).animate().fadeIn(delay: 400.ms, duration: 400.ms),

          const SizedBox(height: 14),

          // Main input
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: Row(
              children: <Widget>[
                // Upload buttons
                _UploadButton(icon: Icons.image_outlined, label: 'Image', onTap: _uploadImage),
                const SizedBox(width: 6),
                _UploadButton(icon: Icons.picture_as_pdf_outlined, label: 'PDF', onTap: _uploadPdf),
                const SizedBox(width: 6),
                _UploadButton(icon: Icons.mic_outlined, label: 'Audio', onTap: _uploadAudio),
                const SizedBox(width: 12),

                // Text input
                Expanded(
                  child: TextField(
                    controller: _controller,
                    minLines: 1,
                    maxLines: 4,
                    decoration: InputDecoration(
                      hintText: 'Paste recruiter message, internship URL, Telegram chat, or upload evidence…',
                      suffixIcon: IconButton(
                        icon: Icon(
                          Icons.arrow_upward,
                          color: isInvestigating ? cs.onSurface.withValues(alpha: 0.3) : cs.primary,
                        ),
                        onPressed: isInvestigating ? null : _submit,
                      ),
                    ),
                    onSubmitted: isInvestigating ? null : (_) => _submit(),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }

  void _fill(String text) {
    setState(() => _controller.text = text);
  }

  void _submit() {
    final String text = _controller.text.trim();
    if (text.isEmpty) return;
    ref.read(investigationControllerProvider.notifier).start(text);
  }

  Future<void> _uploadImage() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.image,
      allowMultiple: false,
    );
    if (result != null && result.files.single.path != null) {
      await ref.read(investigationControllerProvider.notifier).uploadFile(
        result.files.single.path!,
        result.files.single.name,
      );
    }
  }

  Future<void> _uploadPdf() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      allowMultiple: false,
    );
    if (result != null && result.files.single.path != null) {
      await ref.read(investigationControllerProvider.notifier).uploadFile(
        result.files.single.path!,
        result.files.single.name,
      );
    }
  }

  Future<void> _uploadAudio() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.audio,
      allowMultiple: false,
    );
    if (result != null && result.files.single.path != null) {
      await ref.read(investigationControllerProvider.notifier).uploadFile(
        result.files.single.path!,
        result.files.single.name,
      );
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-widgets
// ─────────────────────────────────────────────────────────────────────────────

class _UploadButton extends StatelessWidget {
  const _UploadButton({required this.icon, required this.label, required this.onTap});
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: 'Upload $label',
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.12),
            ),
          ),
          child: Icon(icon, size: 18, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.45)),
        ),
      ),
    );
  }
}

class _ExplainabilityStory extends StatelessWidget {
  const _ExplainabilityStory({required this.summary});
  final String summary;

  @override
  Widget build(BuildContext context) {
    final ColorScheme cs = Theme.of(context).colorScheme;
    final List<String> lines = summary
        .split('\n')
        .where((String s) => s.trim().isNotEmpty)
        .toList();

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 640),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Row(
                children: <Widget>[
                  Icon(Icons.auto_stories, size: 16, color: cs.primary),
                  const SizedBox(width: 8),
                  Text(
                    'Why Hermes flagged this',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(color: cs.primary),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              for (int i = 0; i < lines.length; i++)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 3),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text('•', style: TextStyle(color: cs.primary, fontSize: 14)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          lines[i].replaceFirst(RegExp(r'^[-•]\s*'), ''),
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ),
                    ],
                  ),
                ).animate(delay: Duration(milliseconds: i * 100))
                    .fadeIn(duration: 300.ms)
                    .slideX(begin: -0.02),
            ],
          ),
        ),
      ),
    );
  }
}

class _EvidenceBreakdownList extends StatelessWidget {
  const _EvidenceBreakdownList({required this.breakdown});
  final List<Map<String, Object?>> breakdown;

  @override
  Widget build(BuildContext context) {
    final ColorScheme cs = Theme.of(context).colorScheme;
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 640),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Row(
                children: <Widget>[
                  Icon(Icons.fact_check_outlined, size: 16, color: cs.primary),
                  const SizedBox(width: 8),
                  Text(
                    'Evidence signals',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(color: cs.primary),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              for (int i = 0; i < breakdown.length; i++)
                _EvidenceRow(signal: breakdown[i], index: i),
            ],
          ),
        ),
      ),
    );
  }
}

class _EvidenceRow extends StatelessWidget {
  const _EvidenceRow({required this.signal, required this.index});
  final Map<String, Object?> signal;
  final int index;

  @override
  Widget build(BuildContext context) {
    final String name = (signal['signal']?.toString() ?? 'unknown').replaceAll('_', ' ');
    final int score = (signal['score_contribution'] as num?)?.toInt() ?? 0;
    final double conf = (signal['confidence'] as num?)?.toDouble() ?? 0.0;
    final String source = signal['source']?.toString() ?? 'agent';

    final EvidenceSourceType sourceType = _classifySource(name, source);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: <Widget>[
          EvidenceSourceBadge(type: sourceType),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              name,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500),
            ),
          ),
          Text(
            '+$score pts',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Theme.of(context).colorScheme.primary,
            ),
          ),
          const SizedBox(width: 12),
          Text(
            '${(conf * 100).toStringAsFixed(0)}%',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    ).animate(delay: Duration(milliseconds: index * 80)).fadeIn(duration: 250.ms);
  }

  EvidenceSourceType _classifySource(String name, String source) {
    const Set<String> deterministic = <String>{
      'upi reused', 'reused upi payment id', 'hidden whois', 'newly registered domain',
      'invalid tls', 'suspicious domain age',
    };
    if (deterministic.contains(name)) return EvidenceSourceType.verified;
    if (source.contains('graph') || source.contains('campaign')) return EvidenceSourceType.hybrid;
    return EvidenceSourceType.aiReasoned;
  }
}
