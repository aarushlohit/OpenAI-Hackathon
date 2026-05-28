import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  runApp(const HermesXApp());
}

class HermesXApp extends StatelessWidget {
  const HermesXApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hermes-X',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.dark(
          surface: const Color(0xFF0F0F0F),
          primary: const Color(0xFFF97316),
        ),
        useMaterial3: true,
      ),
      home: const HermesWebView(),
    );
  }
}

class HermesWebView extends StatefulWidget {
  const HermesWebView({super.key});

  @override
  State<HermesWebView> createState() => _HermesWebViewState();
}

class _HermesWebViewState extends State<HermesWebView> {
  late final WebViewController _controller;
  bool _isLoading = true;

  static const String _backendUrl = 'http://localhost:8001';

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFF0F0F0F))
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (_) => setState(() => _isLoading = true),
          onPageFinished: (_) => setState(() => _isLoading = false),
          onWebResourceError: (err) {
            setState(() => _isLoading = false);
          },
        ),
      )
      ..loadRequest(Uri.parse(_backendUrl));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F0F),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_isLoading) _buildSplash(),
        ],
      ),
    );
  }

  Widget _buildSplash() {
    return Container(
      color: const Color(0xFF0F0F0F),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFFF97316), Color(0xFFDC2626)],
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFFF97316).withOpacity(0.3),
                    blurRadius: 32,
                    spreadRadius: 4,
                  )
                ],
              ),
              child: const Icon(Icons.shield_outlined, color: Colors.white, size: 36),
            ),
            const SizedBox(height: 24),
            const Text(
              'Hermes-X',
              style: TextStyle(
                color: Colors.white,
                fontSize: 26,
                fontWeight: FontWeight.w700,
                letterSpacing: -0.5,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Recruitment Scam Investigator',
              style: TextStyle(
                color: Colors.white.withOpacity(0.45),
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 36),
            SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(const Color(0xFFF97316)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
