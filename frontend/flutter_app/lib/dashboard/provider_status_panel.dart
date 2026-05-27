import 'package:flutter/material.dart';

class ProviderStatusPanel extends StatelessWidget {
  const ProviderStatusPanel({required this.status, super.key});

  final String status;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            const Icon(Icons.dns, color: Color(0xFF10B981)),
            const SizedBox(width: 8),
            Text('Provider Infrastructure: $status'),
          ],
        ),
      ),
    );
  }
}
