// FILE: frontend/lib/theme.dart
import 'package:flutter/material.dart';

/// Dark futuristic AI theme
final ThemeData appTheme = ThemeData(
  brightness: Brightness.dark,
  primaryColor: Colors.yellow[700],
  scaffoldBackgroundColor: Colors.black,
  appBarTheme: AppBarTheme(
    backgroundColor: Colors.black,
    foregroundColor: Colors.yellow[700],
    elevation: 4,
    shadowColor: Colors.yellow.withOpacity(0.3),
  ),
  textTheme: const TextTheme(
    bodyLarge: TextStyle(color: Colors.white, fontSize: 16),
    bodyMedium: TextStyle(color: Colors.white70),
    headlineMedium: TextStyle(color: Colors.yellow, fontWeight: FontWeight.bold),
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: Colors.yellow[700],
      foregroundColor: Colors.black,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
  ),
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: Colors.grey[900],
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: Colors.yellow[700]!),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: Colors.yellow[700]!),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: BorderSide(color: Colors.yellow[900]!, width: 2),
    ),
    labelStyle: const TextStyle(color: Colors.white70),
  ),
  cardColor: Colors.grey[850],
  dividerColor: Colors.yellow[700],
);
