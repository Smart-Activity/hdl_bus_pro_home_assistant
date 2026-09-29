# Changelog

All notable changes to this project will be documented in this file.

## 0.2.1 - 2026-09-29

- Fixed cover entities failing to register on recent Home Assistant versions.
- Explicitly marked curtains as assumed-state entities until position feedback
  is implemented.

## 0.2.0 - 2026-09-01

- Added native YAML-configured HDL Buspro curtain entities.
- Added open, close and stop commands using operate code `E3 E0`.
- Fixed raw two-byte operate codes in `buspro.send_message`.

## 0.1.0 - 2026-09-01

- Created an independent repository baseline from `eyesoft/home_assistant_buspro`.
- Retained the original MIT license and attribution.
- Reset the independent project version to 0.1.0.
- Added manual installation and publication guidance.
