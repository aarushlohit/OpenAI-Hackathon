import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  runApp(const DetectiveHermesApp());
}

class DetectiveHermesApp extends StatelessWidget {
  const DetectiveHermesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Detective Hermes Agent',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: const ColorScheme.dark(
          surface: Color(0xFF070807),
          primary: Color(0xFFD6A84F),
        ),
        scaffoldBackgroundColor: const Color(0xFF070807),
        useMaterial3: true,
      ),
      home: const DetectiveHermesWebView(),
    );
  }
}

class DetectiveHermesWebView extends StatefulWidget {
  const DetectiveHermesWebView({super.key});

  @override
  State<DetectiveHermesWebView> createState() => _DetectiveHermesWebViewState();
}

class _DetectiveHermesWebViewState extends State<DetectiveHermesWebView> {
  static final Uri _siteUri = Uri.parse('https://detective-hermes-agent.vercel.app');

  late final WebViewController _controller;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFF070807))
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (_) {
            if (!mounted) return;
            setState(() {
              _loading = true;
              _error = null;
            });
          },
          onPageFinished: (_) {
            if (!mounted) return;
            setState(() => _loading = false);
          },
          onWebResourceError: (WebResourceError error) {
            if (!mounted || error.isForMainFrame == false) return;
            setState(() {
              _loading = false;
              _error = 'Unable to load Detective Hermes Agent. Check your connection.';
            });
          },
        ),
      )
      ..loadRequest(_siteUri);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Stack(
          fit: StackFit.expand,
          children: [
            WebViewWidget(controller: _controller),
            if (_loading) const _LazyLoadingScreen(),
            if (_error != null)
              _LoadError(
                message: _error!,
                onRetry: () => _controller.loadRequest(_siteUri),
              ),
          ],
        ),
      ),
    );
  }
}

class _LazyLoadingScreen extends StatelessWidget {
  const _LazyLoadingScreen();

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: RadialGradient(
          center: Alignment(-0.45, -0.65),
          radius: 1.2,
          colors: [
            Color(0x332D2414),
            Color(0xFF070807),
          ],
        ),
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 78,
              height: 78,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(22),
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFFF6D98B), Color(0xFFB77A22)],
                ),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x44D6A84F),
                    blurRadius: 38,
                    spreadRadius: 4,
                  ),
                ],
              ),
              child: const Text(
                'DH',
                style: TextStyle(
                  color: Color(0xFF17120B),
                  fontSize: 25,
                  fontWeight: FontWeight.w900,
                  letterSpacing: -1,
                ),
              ),
            ),
            const SizedBox(height: 26),
            const Text(
              'Detective Hermes Agent',
              style: TextStyle(
                color: Color(0xFFF4F0E8),
                fontSize: 25,
                fontWeight: FontWeight.w800,
                letterSpacing: -0.4,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Loading investigation workspace',
              style: TextStyle(
                color: Color(0xFFA49B90),
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 32),
            const SizedBox(
              width: 30,
              height: 30,
              child: CircularProgressIndicator(
                strokeWidth: 2.4,
                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFD6A84F)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LoadError extends StatelessWidget {
  const _LoadError({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: const Color(0xEE070807),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 360),
          child: Card(
            color: const Color(0xFF121716),
            child: Padding(
              padding: const EdgeInsets.all(22),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.wifi_off_rounded, color: Color(0xFFD6A84F), size: 36),
                  const SizedBox(height: 14),
                  Text(
                    message,
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Color(0xFFF4F0E8)),
                  ),
                  const SizedBox(height: 18),
                  FilledButton(
                    onPressed: onRetry,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
