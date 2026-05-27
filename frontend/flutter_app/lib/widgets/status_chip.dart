import 'package:flutter/material.dart';

class StatusChip extends StatelessWidget {
  const StatusChip({required this.label, required this.value, super.key});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Chip(label: Text('$label: $value'));
  }
}

