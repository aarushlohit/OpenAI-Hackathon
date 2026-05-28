import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/chat_message.dart';
import 'chat_controller.dart';
import 'widgets/chat_composer.dart';
import 'widgets/hermes_message_bubble.dart';
import 'widgets/user_message_bubble.dart';
import 'widgets/welcome_screen.dart';

/// The main conversational chat view — single scrolling stream like Claude.
class ChatView extends ConsumerStatefulWidget {
  const ChatView({super.key});

  @override
  ConsumerState<ChatView> createState() => _ChatViewState();
}

class _ChatViewState extends ConsumerState<ChatView> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FocusNode _focusNode = FocusNode();

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatControllerProvider);
    final messages = chatState.activeMessages;
    final hasPendingImage = chatState.pendingImageBytes != null;
    final hasPendingAudio = chatState.pendingAudioName != null;
    final isInvestigating =
        messages.any((m) => m.isHermes && m.isInvestigating);

    // Auto-scroll on new messages
    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());

    return Column(
      children: [
        // ── Message stream ───────────────────────────────────────────────
        Expanded(
          child: messages.isEmpty
              ? WelcomeScreen(
                  onSuggestion: (text) {
                    _textController.text = text;
                    _focusNode.requestFocus();
                  },
                )
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.symmetric(
                    vertical: 24,
                    horizontal: 0,
                  ),
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    final msg = messages[index];
                    if (msg.isUser) {
                      return UserMessageBubble(message: msg);
                    }
                    return HermesMessageBubble(message: msg);
                  },
                ),
        ),

        // ── Pending attachment preview ────────────────────────────────────
        if (hasPendingImage || hasPendingAudio)
          _PendingAttachmentBar(
            imageBytes: chatState.pendingImageBytes,
            imageName: chatState.pendingImageName,
            audioName: chatState.pendingAudioName,
            onRemove: () => ref.read(chatControllerProvider.notifier).clearPending(),
          ),

        // ── Chat composer ─────────────────────────────────────────────────
        ChatComposer(
          controller: _textController,
          focusNode: _focusNode,
          isInvestigating: isInvestigating,
          onSend: _handleSend,
          onUploadImage: _uploadImage,
          onUploadFile: _uploadFile,
          onUploadAudio: _uploadAudio,
        ),
      ],
    );
  }

  void _handleSend() {
    final text = _textController.text.trim();
    final chatState = ref.read(chatControllerProvider);
    if (text.isEmpty && chatState.pendingImageBytes == null) return;
    _textController.clear();
    ref.read(chatControllerProvider.notifier).sendMessage(text);
  }

  Future<void> _uploadImage() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.image,
      allowMultiple: false,
      withData: true,
    );
    if (result != null && result.files.single.bytes != null) {
      ref.read(chatControllerProvider.notifier).setPendingImage(
            result.files.single.bytes!,
            result.files.single.name,
          );
    }
  }

  Future<void> _uploadFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'png', 'jpeg'],
      allowMultiple: false,
      withData: true,
    );
    if (result != null && result.files.single.bytes != null) {
      ref.read(chatControllerProvider.notifier).setPendingImage(
            result.files.single.bytes!,
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
      ref.read(chatControllerProvider.notifier).setPendingAudio(
            result.files.single.name,
          );
    }
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Pending Attachment Bar
// ─────────────────────────────────────────────────────────────────────────────

class _PendingAttachmentBar extends StatelessWidget {
  const _PendingAttachmentBar({
    this.imageBytes,
    this.imageName,
    this.audioName,
    required this.onRemove,
  });

  final Uint8List? imageBytes;
  final String? imageName;
  final String? audioName;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 8),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: cs.primary.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          if (imageBytes != null) ...[
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: Image.memory(imageBytes!, height: 40, width: 40, fit: BoxFit.cover),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                imageName ?? 'Image',
                style: const TextStyle(fontSize: 12),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ] else if (audioName != null) ...[
            Icon(Icons.audiotrack, size: 20, color: cs.primary),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                audioName!,
                style: const TextStyle(fontSize: 12),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
          IconButton(
            onPressed: onRemove,
            icon: const Icon(Icons.close, size: 16),
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 200.ms).slideY(begin: 0.1);
  }
}
