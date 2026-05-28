import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Chat composer — bottom input bar with multiline text, upload buttons, send.
class ChatComposer extends StatelessWidget {
  const ChatComposer({
    required this.controller,
    required this.focusNode,
    required this.isInvestigating,
    required this.onSend,
    required this.onUploadImage,
    required this.onUploadFile,
    required this.onUploadAudio,
    super.key,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final bool isInvestigating;
  final VoidCallback onSend;
  final VoidCallback onUploadImage;
  final VoidCallback onUploadFile;
  final VoidCallback onUploadAudio;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
      decoration: BoxDecoration(
        color: const Color(0xFF1B1B1F),
        border: Border(
          top: BorderSide(color: cs.onSurface.withValues(alpha: 0.08)),
        ),
      ),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 800),
        child: Center(
          child: Container(
            decoration: BoxDecoration(
              color: const Color(0xFF24242A),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isInvestigating
                    ? cs.primary.withValues(alpha: 0.3)
                    : cs.onSurface.withValues(alpha: 0.12),
              ),
            ),
            child: Column(
              children: [
                // Text input
                TextField(
                  controller: controller,
                  focusNode: focusNode,
                  minLines: 1,
                  maxLines: 6,
                  enabled: !isInvestigating,
                  style: TextStyle(
                    fontSize: 14,
                    color: cs.onSurface.withValues(alpha: 0.9),
                    height: 1.5,
                  ),
                  decoration: InputDecoration(
                    hintText: isInvestigating
                        ? 'Investigation in progress...'
                        : 'Paste recruiter message, internship URL, or describe your situation…',
                    hintStyle: TextStyle(
                      fontSize: 14,
                      color: cs.onSurface.withValues(alpha: 0.3),
                    ),
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.fromLTRB(16, 14, 16, 8),
                  ),
                  onSubmitted: isInvestigating ? null : (_) => onSend(),
                ),

                // Bottom toolbar
                Padding(
                  padding: const EdgeInsets.fromLTRB(8, 0, 8, 8),
                  child: Row(
                    children: [
                      // Upload buttons
                      _ToolbarButton(
                        icon: Icons.image_outlined,
                        tooltip: 'Upload image or screenshot',
                        onTap: isInvestigating ? null : onUploadImage,
                      ),
                      _ToolbarButton(
                        icon: Icons.attach_file_outlined,
                        tooltip: 'Upload PDF or document',
                        onTap: isInvestigating ? null : onUploadFile,
                      ),
                      _ToolbarButton(
                        icon: Icons.mic_outlined,
                        tooltip: 'Upload audio',
                        onTap: isInvestigating ? null : onUploadAudio,
                      ),

                      const Spacer(),

                      // Investigating indicator
                      if (isInvestigating)
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: Text(
                            'Investigating...',
                            style: TextStyle(
                              fontSize: 11,
                              color: cs.primary.withValues(alpha: 0.6),
                            ),
                          ).animate(onPlay: (c) => c.repeat(reverse: true))
                              .fadeIn(duration: 600.ms),
                        ),

                      // Send button
                      GestureDetector(
                        onTap: isInvestigating ? null : onSend,
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 34,
                          height: 34,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: isInvestigating
                                ? cs.onSurface.withValues(alpha: 0.1)
                                : cs.primary,
                          ),
                          child: Icon(
                            Icons.arrow_upward_rounded,
                            size: 18,
                            color: isInvestigating
                                ? cs.onSurface.withValues(alpha: 0.3)
                                : Colors.black,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ToolbarButton extends StatelessWidget {
  const _ToolbarButton({
    required this.icon,
    required this.tooltip,
    this.onTap,
  });

  final IconData icon;
  final String tooltip;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Tooltip(
      message: tooltip,
      child: IconButton(
        onPressed: onTap,
        icon: Icon(
          icon,
          size: 18,
          color: onTap != null
              ? cs.onSurface.withValues(alpha: 0.4)
              : cs.onSurface.withValues(alpha: 0.15),
        ),
        padding: const EdgeInsets.all(6),
        constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
      ),
    );
  }
}
