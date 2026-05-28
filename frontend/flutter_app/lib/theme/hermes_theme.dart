import 'package:flutter/material.dart';

/// Hermes-X design system.
///
/// Two palettes:
/// - **warm** (default) — Claude-inspired, human-first
/// - **soc**  — technical SOC dashboard (Dev Mode)
class HermesTheme {
  HermesTheme._();

  // ── Warm palette ─────────────────────────────────────────────────────────
  static const Color _warmBg       = Color(0xFF1E1B18);
  static const Color _warmSurface  = Color(0xFF2A2623);
  static const Color _warmCard     = Color(0xFF322E2A);
  static const Color _warmAccent   = Color(0xFFD97706);
  static const Color _warmText     = Color(0xFFF5F5F4);
  static const Color _warmMuted    = Color(0xFF8A8480);
  static const Color _warmDanger   = Color(0xFFDC2626);
  static const Color _warmSuccess  = Color(0xFF10B981);
  static const Color _warmInfo     = Color(0xFF60A5FA);

  // ── SOC palette ──────────────────────────────────────────────────────────
  static const Color _socBg        = Color(0xFF0B1020);
  static const Color _socSurface   = Color(0xFF111827);
  static const Color _socCyan      = Color(0xFF22D3EE);

  // ── Shared typography ────────────────────────────────────────────────────
  static const String _fontFamily  = 'Inter';

  /// Default warm theme — human-first, friendly.
  static ThemeData dark() => _build(
        bg: _warmBg,
        surface: _warmSurface,
        card: _warmCard,
        primary: _warmAccent,
        text: _warmText,
        muted: _warmMuted,
        danger: _warmDanger,
        success: _warmSuccess,
        info: _warmInfo,
        cardRadius: 16,
        inputRadius: 24,
        cardElevation: 2,
      );

  /// Technical SOC theme — Dev Mode.
  static ThemeData soc() => _build(
        bg: _socBg,
        surface: _socSurface,
        card: _socSurface.withValues(alpha: 0.86),
        primary: _socCyan,
        text: _warmText,
        muted: _warmMuted,
        danger: const Color(0xFFEF4444),
        success: _warmSuccess,
        info: _socCyan,
        cardRadius: 8,
        inputRadius: 8,
        cardElevation: 8,
      );

  static ThemeData _build({
    required Color bg,
    required Color surface,
    required Color card,
    required Color primary,
    required Color text,
    required Color muted,
    required Color danger,
    required Color success,
    required Color info,
    required double cardRadius,
    required double inputRadius,
    required double cardElevation,
  }) {
    return ThemeData(
      brightness: Brightness.dark,
      fontFamily: _fontFamily,
      scaffoldBackgroundColor: bg,
      cardTheme: CardThemeData(
        color: card,
        elevation: cardElevation,
        shadowColor: primary.withValues(alpha: 0.10),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(cardRadius),
        ),
      ),
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        brightness: Brightness.dark,
        primary: primary,
        surface: surface,
        error: danger,
        secondary: const Color(0xFFF59E0B),
        tertiary: success,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: bg,
        elevation: 0,
        titleTextStyle: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: text,
        ),
      ),
      textTheme: TextTheme(
        headlineLarge: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: text),
        headlineMedium: TextStyle(fontSize: 22, fontWeight: FontWeight.w600, color: text),
        headlineSmall: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: text),
        titleLarge: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: text),
        titleMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: text),
        bodyLarge: TextStyle(fontSize: 15, color: text),
        bodyMedium: TextStyle(fontSize: 13, color: text.withValues(alpha: 0.80)),
        bodySmall: TextStyle(fontSize: 11, color: muted),
        labelSmall: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: muted, letterSpacing: 0.8),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: BorderSide(color: primary, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: BorderSide(color: muted.withValues(alpha: 0.25)),
        ),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(inputRadius)),
        hintStyle: TextStyle(color: muted.withValues(alpha: 0.55)),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: const Color(0xFF1E1B18),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(inputRadius)),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primary,
          side: BorderSide(color: primary.withValues(alpha: 0.5)),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(inputRadius)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        ),
      ),
      dividerTheme: DividerThemeData(color: muted.withValues(alpha: 0.12)),
      useMaterial3: true,
    );
  }
}
