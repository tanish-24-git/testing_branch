// FILE: frontend/lib/pages/home_page.dart
import 'package:flutter/material.dart';
import 'package:frontend/pages/chat_page.dart';
import 'package:frontend/pages/email_page.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Map<String, dynamic>> workflows = [
      {"title": "Chat with AI", "icon": Icons.chat, "page": const ChatPage()},
      {"title": "Smart Email", "icon": Icons.email, "page": const EmailPage()},
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('AI Agent Home')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: ListView.builder(
          itemCount: workflows.length,
          itemBuilder: (context, index) {
            final workflow = workflows[index];
            return AnimatedSwitcher(
              duration: const Duration(milliseconds: 500),
              transitionBuilder: (child, animation) {
                final offsetAnimation = Tween<Offset>(
                  begin: const Offset(0.2, 0.2),
                  end: Offset.zero,
                ).animate(animation);
                return FadeTransition(
                  opacity: animation,
                  child: SlideTransition(position: offsetAnimation, child: child),
                );
              },
              child: Card(
                key: ValueKey(workflow["title"]),
                margin: const EdgeInsets.symmetric(vertical: 12),
                child: ListTile(
                  leading: Icon(workflow["icon"], color: Colors.yellow[700], size: 32),
                  title: Text(workflow["title"], style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  trailing: const Icon(Icons.arrow_forward_ios, color: Colors.white54),
                  onTap: () {
                    Navigator.push(
                      context,
                      PageRouteBuilder(
                        transitionDuration: const Duration(milliseconds: 500),
                        pageBuilder: (context, animation, secondaryAnimation) =>
                            SlideTransition(
                          position: Tween<Offset>(
                            begin: const Offset(1, 0),
                            end: Offset.zero,
                          ).animate(animation),
                          child: workflow["page"],
                        ),
                      ),
                    );
                  },
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
