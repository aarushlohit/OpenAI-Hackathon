import 'package:flutter/material.dart';

class HermesTheme {
  static ThemeData dark() {
    const background = Color(0xFF0B1020);
    const surface = Color(0xFF111827);
    const cyan = Color(0xFF22D3EE);
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      cardTheme: CardThemeData(
        color: surface.withValues(alpha: 0.86),
        elevation: 8,
        shadowColor: cyan.withValues(alpha: 0.22),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      colorScheme: ColorScheme.fromSeed(
        seedColor: cyan,
        brightness: Brightness.dark,
        primary: cyan,
        surface: surface,
        error: const Color(0xFFEF4444),
        secondary: const Color(0xFFF59E0B),
        tertiary: const Color(0xFF10B981),
      ),
      inputDecorationTheme: InputDecorationTheme(
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: cyan),
        ),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
      ),
      useMaterial3: true,
    );
  }
}
