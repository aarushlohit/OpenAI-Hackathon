import 'package:flutter/material.dart';

import 'dashboard/dashboard_screen.dart';
import 'theme/hermes_theme.dart';

void main() {
  runApp(const HermesApp());
}

class HermesApp extends StatelessWidget {
  const HermesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hermes-X',
      debugShowCheckedModeBanner: false,
      theme: HermesTheme.dark(),
      home: const DashboardScreen(),
    );
  }
}

