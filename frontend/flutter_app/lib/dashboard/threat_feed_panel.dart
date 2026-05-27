import 'package:flutter/material.dart';

class ThreatFeedPanel extends StatelessWidget {
  const ThreatFeedPanel({required this.items, super.key});

  final List<String> items;

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) => ListTile(
        dense: true,
        leading: const Icon(Icons.warning_amber),
        title: Text(items[index]),
      ),
    );
  }
}

