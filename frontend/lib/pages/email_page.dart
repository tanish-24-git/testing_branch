// FILE: frontend/lib/pages/email_page.dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

String getBaseUrl() {
  if (Platform.isWindows) {
    return 'http://127.0.0.1:8001';
  } else {
    return 'http://localhost:8001';
  }
}

class EmailPage extends StatefulWidget {
  const EmailPage({super.key});

  @override
  State<EmailPage> createState() => _EmailPageState();
}

class _EmailPageState extends State<EmailPage> {
  int _selectedIndex = 0; // 0: Inbox, 1: Sent, 2: Scheduled, 3: Trash
  List<dynamic> _emails = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _fetchEmails();
  }

  Future<void> _fetchEmails() async {
    setState(() => _isLoading = true);

    final labels = ["INBOX", "SENT", "SCHEDULED", "TRASH"];
    final String label = labels[_selectedIndex];

    try {
      final response = await http.get(
        Uri.parse('${getBaseUrl()}/email/check?count=10&label=$label'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() => _emails = data['emails']);
      } else {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Error: ${response.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _replyWithAI(String emailId) async {
    try {
      final response = await http.post(
        Uri.parse('${getBaseUrl()}/email/auto-reply'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email_id': emailId}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final aiDraft = data['draft'] ?? "Generated reply text...";

        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ComposeEmailPage(
              initialBody: aiDraft,
              replyingTo: emailId,
            ),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: ${response.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  Widget buildEmailList() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_emails.isEmpty) {
      return const Center(child: Text("No emails found."));
    }

    return ListView.builder(
      itemCount: _emails.length,
      itemBuilder: (context, index) {
        final email = _emails[index];
        return AnimatedSwitcher(
          duration: const Duration(milliseconds: 400),
          transitionBuilder: (child, animation) {
            final offsetAnimation = Tween<Offset>(
              begin: const Offset(0.1, 0),
              end: Offset.zero,
            ).animate(animation);
            return FadeTransition(
              opacity: animation,
              child: SlideTransition(position: offsetAnimation, child: child),
            );
          },
          child: Card(
            key: ValueKey(email['id']),
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: ListTile(
              title: Text(email['subject'] ?? 'No Subject'),
              subtitle: Text(
                  '${email['from'] ?? 'Unknown'} - ${email['snippet'] ?? ''}'),
              trailing: IconButton(
                icon: const Icon(Icons.reply, color: Colors.blue),
                onPressed: () => _replyWithAI(email['id']),
              ),
            ),
          ),
        );
      },
    );
  }

  void _openComposePage() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ComposeEmailPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Left NavigationRail
          NavigationRail(
            backgroundColor: Colors.grey[900],
            selectedIndex: _selectedIndex,
            onDestinationSelected: (index) {
              setState(() => _selectedIndex = index);
              _fetchEmails();
            },
            labelType: NavigationRailLabelType.all,
            unselectedIconTheme: const IconThemeData(color: Colors.white70),
            selectedIconTheme: const IconThemeData(color: Colors.white),
            selectedLabelTextStyle: const TextStyle(color: Colors.white),
            unselectedLabelTextStyle: const TextStyle(color: Colors.white70),
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.inbox),
                label: Text("Inbox"),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.send),
                label: Text("Sent"),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.schedule),
                label: Text("Scheduled"),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.delete),
                label: Text("Trash"),
              ),
            ],
          ),

          // Main email list
          Expanded(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 400),
              transitionBuilder: (child, animation) {
                final slideAnimation = Tween<Offset>(
                  begin: const Offset(0, 0.05),
                  end: Offset.zero,
                ).animate(animation);
                return FadeTransition(
                  opacity: animation,
                  child: SlideTransition(position: slideAnimation, child: child),
                );
              },
              child: buildEmailList(),
            ),
          ),
        ],
      ),

      floatingActionButton: FloatingActionButton(
        onPressed: _openComposePage,
        backgroundColor: Colors.blue,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }
}

// ✅ Compose Page with AI-generated drafts support
class ComposeEmailPage extends StatefulWidget {
  final String? initialBody;
  final String? replyingTo;

  const ComposeEmailPage({super.key, this.initialBody, this.replyingTo});

  @override
  State<ComposeEmailPage> createState() => _ComposeEmailPageState();
}

class _ComposeEmailPageState extends State<ComposeEmailPage> {
  final TextEditingController _toController = TextEditingController();
  final TextEditingController _subjectController = TextEditingController();
  final TextEditingController _bodyController = TextEditingController();
  final TextEditingController _promptController = TextEditingController();
  final TextEditingController _scheduleTimeController = TextEditingController();

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    if (widget.initialBody != null) {
      _bodyController.text = widget.initialBody!;
    }
  }

  Future<void> _generateBodyWithLLM() async {
    final String prompt = _promptController.text.trim();
    if (prompt.isEmpty) return;

    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse('${getBaseUrl()}/command'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'command': 'Generate email body: $prompt'}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _bodyController.text = data['result'];
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: ${response.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _sendEmail({bool isSchedule = false}) async {
    final Map<String, dynamic> body = {
      'to': _toController.text,
      'subject': _subjectController.text,
      'body': _bodyController.text,
    };
    if (isSchedule) body['scheduled_time'] = _scheduleTimeController.text;

    try {
      final response = await http.post(
        Uri.parse(isSchedule
            ? '${getBaseUrl()}/email/schedule'
            : '${getBaseUrl()}/email/send'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Success')));
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Error: ${response.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Compose Email")),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16),
              child: ListView(
                children: [
                  TextField(
                    controller: _toController,
                    decoration: const InputDecoration(labelText: 'To'),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _subjectController,
                    decoration: const InputDecoration(labelText: 'Subject'),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _bodyController,
                    decoration: const InputDecoration(labelText: 'Body'),
                    maxLines: 6,
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _promptController,
                    decoration: const InputDecoration(
                        labelText: 'LLM Prompt for Body'),
                  ),
                  ElevatedButton(
                      onPressed: _generateBodyWithLLM,
                      child: const Text('Generate with AI')),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _scheduleTimeController,
                    decoration: const InputDecoration(
                        labelText: 'Schedule Time (ISO)'),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ElevatedButton(
                          onPressed: () => _sendEmail(),
                          child: const Text('Send')),
                      ElevatedButton(
                          onPressed: () => _sendEmail(isSchedule: true),
                          child: const Text('Schedule')),
                    ],
                  ),
                ],
              ),
            ),
    );
  }
}
