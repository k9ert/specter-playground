# MockUI Documentation

## Screen Reference

See [screens/](screens/) for captured screenshots, widget trees, and descriptions.

Regenerate with: `sim_cli.py explore`

## Navigation Structure

```
main
├── Scan QR
├── Import Seed From SmartCard
├── Add Wallet (add_wallet)
│   ├── Generate New Seedphrase (generate_seedphrase)
│   │   └── set_passphrase
│   └── Import from SmartCard/QR/Flash/Keyboard (manage_seedphrase)
├── Manage Device (manage_device)
│   ├── Manage Firmware (manage_firmware)
│   ├── Manage Security Features (manage_security)
│   ├── Enable/Disable Interfaces (interfaces)
│   ├── Manage Display (action_screen)
│   ├── Manage Sounds (action_screen)
│   └── Wipe Device (action_screen)
├── Manage Storage (manage_storage)
│   ├── Manage internal flash
│   └── Manage SmartCard
└── Manage Backups (manage_backups)
    ├── Backup to SD Card
    ├── Restore from SD Card
    └── Remove from SD Card
```

## Screens

| Menu ID | Title | Description |
|---------|-------|-------------|
| [main](screens/main/) | Main Menu | Entry point with all primary actions |
| [add_wallet](screens/add_wallet/) | Add Wallet | Create or import a wallet seed |
| [generate_seedphrase](screens/generate_seedphrase/) | Generate Seedphrase | Create new BIP39 seed with wallet config |
| [set_passphrase](screens/set_passphrase/) | Set Passphrase | Add BIP39 passphrase to seed |
| [manage_seedphrase](screens/manage_seedphrase/) | Manage Seedphrase | View, backup, restore seed operations |
| [manage_device](screens/manage_device/) | Manage Device | Device settings and configuration |
| [manage_firmware](screens/manage_firmware/) | Manage Firmware | Firmware version and updates |
| [manage_security](screens/manage_security/) | Security Features | PIN, self-test, duress settings |
| [interfaces](screens/interfaces/) | Interfaces | Enable/disable QR, USB, SD, SmartCard |
| [manage_storage](screens/manage_storage/) | Manage Storage | Internal flash and SmartCard management |
| [manage_backups](screens/manage_backups/) | Manage Backups | SD card backup and restore |
| [locked](screens/locked/) | Device Locked | PIN entry to unlock device |

## State-Dependent Screens

Some screens only appear when certain state conditions are met:
- `manage_wallet` - Requires active wallet
- `change_wallet` - Requires registered wallets
- `connect_sw_wallet` - Wallet connection flow
- `locked` - When device is locked
