import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'features/runtime/mvp_status_screen.dart';
import 'theme/hermes_theme.dart';

void main() {
  runApp(const ProviderScope(child: HermesApp()));
}

class HermesApp extends StatelessWidget {
  const HermesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hermes-X',
      debugShowCheckedModeBanner: false,
      theme: HermesTheme.dark(),
      home: const MvpStatusScreen(),
    );
  }
}
