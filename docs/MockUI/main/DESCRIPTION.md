# Main Menu

## Purpose
Entry point for all device operations. User lands here after unlock.

## User Actions
- **Scan QR** - Scan QR code for PSBT signing or wallet import
- **Import Seed From SmartCard** - Quick import from inserted SmartCard
- **Add Wallet** - Create new or import existing wallet
- **Manage Device** - Device settings (firmware, security, display)
- **Manage Storage** - Internal flash and SmartCard management

## State Requirements
- `is_locked: false` - Device must be unlocked
- No wallet required for basic operations
