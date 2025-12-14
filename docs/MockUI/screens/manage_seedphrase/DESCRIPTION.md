# Manage Seedphrase

## Purpose
Operations on the currently loaded seed phrase.

## User Actions
- **Show Seedphrase** - Display mnemonic words
- **Store to SmartCard** - Save seed to SmartCard
- **Store to internal Flash** - Save seed to device
- **Delete from SmartCard** - Remove seed from SmartCard
- **Delete from internal Flash** - Remove seed from device
- **Delete from all storage** - Wipe seed everywhere
- **Derive new via BIP-85** - Create child seed using BIP-85

## State Requirements
Requires `seed_loaded: true`
