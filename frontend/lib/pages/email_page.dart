// FILE: frontend/lib/pages/email_page.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class EmailPage extends StatefulWidget {
  const EmailPage({super.key});

  @override
  State<EmailPage> createState() => _EmailPageState();
}

class _EmailPageState extends State<EmailPage> {
  int _selectedIndex = 0;  // 0: Inbox, 1: Sent
  List<dynamic> _emails = [];
  bool _isLoading = false;

  final TextEditingController _toController = TextEditingController();
  final TextEditingController _subjectController = TextEditingController();
  final TextEditingController _bodyController = TextEditingController();
  final TextEditingController _promptController = TextEditingController();
  final TextEditingController _scheduleTimeController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchEmails();
  }

  Future<void> _fetchEmails() async {
    setState(() {
      _isLoading = true;
    });

    final String label = _selectedIndex == 0 ? 'INBOX' : 'SENT';
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/email/check?count=10&label=$label'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _emails = data['emails'];
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${response.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _generateBodyWithLLM() async {
    final String prompt = _promptController.text.trim();
    if (prompt.isEmpty) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/command'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'command': 'Generate email body: $prompt'}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _bodyController.text = data['result'];
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${response.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _sendEmail({bool isSchedule = false}) async {
    final Map<String, dynamic> body = {
      'to': _toController.text,
      'subject': _subjectController.text,
      'body': _bodyController.text,
    };
    if (isSchedule) {
      body['scheduled_time'] = _scheduleTimeController.text;
    }

    try {
      final response = await http.post(
        Uri.parse(isSchedule ? 'http://localhost:8000/email/schedule' : 'http://localhost:8000/email/send'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Success')));
        _clearForms();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${response.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  Future<void> _autoReply(String emailId) async {
    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/email/auto-reply'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email_id': emailId}),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Auto-reply sent')));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${response.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  void _clearForms() {
    _toController.clear();
    _subjectController.clear();
    _bodyController.clear();
    _promptController.clear();
    _scheduleTimeController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Email'),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
          _fetchEmails();
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.inbox), label: 'Inbox'),
          BottomNavigationBarItem(icon: Icon(Icons.send), label: 'Sent'),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    itemCount: _emails.length,
                    itemBuilder: (context, index) {
                      final email = _emails[index];
                      return Card(
                        child: ListTile(
                          title: Text(email['subject'] ?? 'No Subject'),
                          subtitle: Text('${email['from'] ?? 'Unknown'} - ${email['snippet'] ?? ''}'),
                          trailing: IconButton(
                            icon: const Icon(Icons.reply),
                            onPressed: () => _autoReply(email['id']),
                          ),
                        ),
                      );
                    },
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    children: [
                      TextField(controller: _toController, decoration: const InputDecoration(labelText: 'To')),
                      TextField(controller: _subjectController, decoration: const InputDecoration(labelText: 'Subject')),
                      TextField(controller: _bodyController, decoration: const InputDecoration(labelText: 'Body'), maxLines: 3),
                      TextField(controller: _promptController, decoration: const InputDecoration(labelText: 'LLM Prompt for Body')),
                      ElevatedButton(onPressed: _generateBodyWithLLM, child: const Text('Generate Body with LLM')),
                      TextField(controller: _scheduleTimeController, decoration: const InputDecoration(labelText: 'Schedule Time (ISO)')),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          ElevatedButton(onPressed: () => _sendEmail(), child: const Text('Send')),
                          ElevatedButton(onPressed: () => _sendEmail(isSchedule: true), child: const Text('Schedule')),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }
}