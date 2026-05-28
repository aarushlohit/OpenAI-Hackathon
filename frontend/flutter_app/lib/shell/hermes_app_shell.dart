import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../dashboard/dashboard_screen.dart';
import '../features/chat/chat_controller.dart';
import '../features/chat/chat_view.dart';
import '../models/chat_message.dart';
import '../theme/hermes_theme.dart';

/// Global state: dev mode on/off.
final devModeProvider = StateProvider<bool>((ref) => false);

/// Root app shell — Claude-style sidebar + conversational main area.
/// Dev mode switches to full SOC dashboard.
class HermesAppShell extends ConsumerWidget {
  const HermesAppShell({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final bool devMode = ref.watch(devModeProvider);

    return AnimatedTheme(
      data: devMode ? HermesTheme.soc() : HermesTheme.dark(),
      duration: const Duration(milliseconds: 400),
      child: Scaffold(
        backgroundColor: const Color(0xFF1B1B1F),
        body: Row(
          children: <Widget>[
            // ── Sidebar ───────────────────────────────────────────────────
            _Sidebar(devMode: devMode),

            // ── Main content ──────────────────────────────────────────────
            Expanded(
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 400),
                transitionBuilder: (Widget child, Animation<double> animation) {
                  return FadeTransition(opacity: animation, child: child);
                },
                child: devMode
                    ? const DashboardScreen(key: ValueKey<String>('soc'))
                    : const ChatView(key: ValueKey<String>('chat')),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Sidebar
// ─────────────────────────────────────────────────────────────────────────────

class _Sidebar extends ConsumerWidget {
  const _Sidebar({required this.devMode});
  final bool devMode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final chatState = ref.watch(chatControllerProvider);
    final sessions = chatState.sessions;
    final activeId = chatState.activeSessionId;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 400),
      width: 232,
      color: const Color(0xFF141417),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          // ── Brand ───────────────────────────────────────────────────────
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 20, 16, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: <Widget>[
                    Container(
                      width: 28,
                      height: 28,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFFD97706).withValues(alpha: 0.15),
                        border: Border.all(
                          color: const Color(0xFFD97706).withValues(alpha: 0.4),
                        ),
                      ),
                      child: const Icon(Icons.shield,
                          color: Color(0xFFD97706), size: 15),
                    ),
                    const SizedBox(width: 10),
                    const Text(
                      'Hermes-X',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFD97706),
                        letterSpacing: 0.3,
                      ),
                    ),
                  ],
                ).animate().fadeIn(duration: 400.ms),

                const SizedBox(height: 4),
                Text(
                  'Cyber fraud investigations',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.white.withValues(alpha: 0.3),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // ── New Investigation ────────────────────────────────────────────
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: _NewChatButton(
              onTap: () => ref.read(chatControllerProvider.notifier).newSession(),
            ),
          ),

          const SizedBox(height: 16),

          // ── Navigation ───────────────────────────────────────────────────
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Column(
              children: [
                _NavItem(
                  icon: Icons.history,
                  label: 'Investigation History',
                  onTap: () {},
                ),
                _NavItem(
                  icon: Icons.bookmark_border,
                  label: 'Saved Reports',
                  onTap: () {},
                ),
                _NavItem(
                  icon: Icons.warning_amber_rounded,
                  label: 'Threat Feed',
                  onTap: () {},
                ),
                _NavItem(
                  icon: Icons.settings_outlined,
                  label: 'Settings',
                  onTap: () {},
                ),
              ],
            ),
          ),

          if (sessions.isNotEmpty) ...[
            const SizedBox(height: 16),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                'RECENT',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: Colors.white.withValues(alpha: 0.25),
                  letterSpacing: 1.2,
                ),
              ),
            ),
            const SizedBox(height: 6),

            // ── Session history list ────────────────────────────────────
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                itemCount: sessions.length,
                itemBuilder: (context, index) {
                  final session = sessions[index];
                  return _SessionTile(
                    session: session,
                    isActive: session.id == activeId,
                    onTap: () => ref
                        .read(chatControllerProvider.notifier)
                        .selectSession(session.id),
                  );
                },
              ),
            ),
          ] else
            const Spacer(),

          // ── Bottom: Dev Mode + Provider health ────────────────────────
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                _ProviderHealthBadge(),
                const SizedBox(height: 8),
                _DevModeToggle(active: devMode),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// New chat button
// ─────────────────────────────────────────────────────────────────────────────

class _NewChatButton extends StatelessWidget {
  const _NewChatButton({required this.onTap});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: const Color(0xFFD97706).withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
              color: const Color(0xFFD97706).withValues(alpha: 0.25)),
        ),
        child: Row(
          children: const [
            Icon(Icons.add, size: 15, color: Color(0xFFD97706)),
            SizedBox(width: 8),
            Text(
              'New Investigation',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: Color(0xFFD97706),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Nav item
// ─────────────────────────────────────────────────────────────────────────────

class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.icon,
    required this.label,
    required this.onTap,
  });
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        child: Row(
          children: [
            Icon(icon, size: 15, color: Colors.white.withValues(alpha: 0.35)),
            const SizedBox(width: 10),
            Text(
              label,
              style: TextStyle(
                fontSize: 13,
                color: Colors.white.withValues(alpha: 0.45),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Session tile
// ─────────────────────────────────────────────────────────────────────────────

class _SessionTile extends StatelessWidget {
  const _SessionTile({
    required this.session,
    required this.isActive,
    required this.onTap,
  });
  final ChatSession session;
  final bool isActive;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final severityColor = _severityColor(session.severity);

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 1),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
          color: isActive
              ? const Color(0xFFD97706).withValues(alpha: 0.08)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            if (severityColor != null)
              Container(
                width: 6,
                height: 6,
                margin: const EdgeInsets.only(right: 8),
                decoration:
                    BoxDecoration(shape: BoxShape.circle, color: severityColor),
              )
            else
              const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    session.title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 12,
                      color: isActive
                          ? Colors.white.withValues(alpha: 0.85)
                          : Colors.white.withValues(alpha: 0.5),
                      fontWeight:
                          isActive ? FontWeight.w500 : FontWeight.normal,
                    ),
                  ),
                  Text(
                    _formatDate(session.createdAt),
                    style: TextStyle(
                      fontSize: 10,
                      color: Colors.white.withValues(alpha: 0.25),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color? _severityColor(String? severity) {
    if (severity == null) return null;
    switch (severity.toLowerCase()) {
      case 'critical':
        return const Color(0xFFDC2626);
      case 'high':
        return const Color(0xFFF97316);
      case 'medium':
        return const Color(0xFFF59E0B);
      case 'low':
        return const Color(0xFF16A34A);
      default:
        return null;
    }
  }

  String _formatDate(DateTime d) {
    final now = DateTime.now();
    if (now.difference(d).inHours < 24) {
      return '${d.hour.toString().padLeft(2, '0')}:${d.minute.toString().padLeft(2, '0')}';
    }
    return '${d.day}/${d.month}';
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Provider health badge
// ─────────────────────────────────────────────────────────────────────────────

class _ProviderHealthBadge extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.03),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: Color(0xFF16A34A),
            ),
          ).animate(onPlay: (c) => c.repeat(reverse: true))
              .fadeIn(duration: 1200.ms),
          const SizedBox(width: 7),
          Text(
            'NVIDIA Nemotron Online',
            style: TextStyle(
              fontSize: 10,
              color: Colors.white.withValues(alpha: 0.3),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Dev Mode toggle
// ─────────────────────────────────────────────────────────────────────────────

class _DevModeToggle extends ConsumerWidget {
  const _DevModeToggle({required this.active});
  final bool active;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return InkWell(
      onTap: () => ref.read(devModeProvider.notifier).state = !active,
      borderRadius: BorderRadius.circular(8),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
          color: active
              ? const Color(0xFFD97706).withValues(alpha: 0.1)
              : Colors.white.withValues(alpha: 0.03),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: active
                ? const Color(0xFFD97706).withValues(alpha: 0.4)
                : Colors.white.withValues(alpha: 0.08),
          ),
        ),
        child: Row(
          children: <Widget>[
            Icon(
              active ? Icons.terminal : Icons.code,
              size: 13,
              color: active
                  ? const Color(0xFFD97706)
                  : Colors.white.withValues(alpha: 0.3),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                active ? 'DEV MODE ON' : 'Dev Mode',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: active ? FontWeight.bold : FontWeight.w400,
                  color: active
                      ? const Color(0xFFD97706)
                      : Colors.white.withValues(alpha: 0.3),
                  letterSpacing: active ? 0.8 : 0,
                ),
              ),
            ),
            AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              width: 26,
              height: 13,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(7),
                color: active
                    ? const Color(0xFFD97706)
                    : Colors.white.withValues(alpha: 0.1),
              ),
              alignment:
                  active ? Alignment.centerRight : Alignment.centerLeft,
              padding: const EdgeInsets.all(1.5),
              child: Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: active
                      ? const Color(0xFF141417)
                      : Colors.white.withValues(alpha: 0.25),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
