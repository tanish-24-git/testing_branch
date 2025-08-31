// FILE: frontend/lib/theme.dart
import 'package:flutter/material.dart';

final ThemeData appTheme = ThemeData(
  brightness: Brightness.dark,
  primaryColor: Colors.yellow[700],
  scaffoldBackgroundColor: Colors.black,
  appBarTheme: AppBarTheme(
    backgroundColor: Colors.black,
    foregroundColor: Colors.yellow[700],
  ),
  textTheme: const TextTheme(
    bodyLarge: TextStyle(color: Colors.white),
    bodyMedium: TextStyle(color: Colors.white70),
    headlineMedium: TextStyle(color: Colors.yellow),
  ),
  buttonTheme: ButtonThemeData(
    buttonColor: Colors.yellow[700],
    textTheme: ButtonTextTheme.primary,
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: Colors.yellow[700],
      foregroundColor: Colors.black,
    ),
  ),
  textButtonTheme: TextButtonThemeData(
    style: TextButton.styleFrom(
      foregroundColor: Colors.yellow[700],
    ),
  ),
  inputDecorationTheme: InputDecorationTheme(
    border: OutlineInputBorder(
      borderSide: BorderSide(color: Colors.yellow[700]!),
    ),
    enabledBorder: OutlineInputBorder(
      borderSide: BorderSide(color: Colors.yellow[700]!),
    ),
    focusedBorder: OutlineInputBorder(
      borderSide: BorderSide(color: Colors.yellow[900]!, width: 2),
    ),
    labelStyle: const TextStyle(color: Colors.white70),
  ),
  cardColor: Colors.grey[900],
  dividerColor: Colors.yellow[700],
);