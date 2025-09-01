
// FILE: frontend/lib/pages/home_page.dart (removed Browser button)
import 'package:flutter/material.dart';
import 'package:frontend/pages/chat_page.dart';
import 'package:frontend/pages/email_page.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Agent Home'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const ChatPage()),
                );
              },
              child: const Text('Go to Chatbot'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const EmailPage()),
                );
              },
              child: const Text('Go to Email'),
            ),
          ],
        ),
      ),
    );
  }
}