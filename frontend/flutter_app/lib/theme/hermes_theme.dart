import 'package:flutter/material.dart';

class HermesTheme {
  static ThemeData dark() {
    const background = Color(0xFF071014);
    const surface = Color(0xFF0D1B20);
    const cyan = Color(0xFF00D1FF);
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      colorScheme: ColorScheme.fromSeed(
        seedColor: cyan,
        brightness: Brightness.dark,
        surface: surface,
      ),
      useMaterial3: true,
    );
  }
}

