# MockUI Screen Documentation

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
| [main](main/) | Main Menu | Entry point with all primary actions |
| [add_wallet](add_wallet/) | Add Wallet | Create or import a wallet seed |
| [generate_seedphrase](generate_seedphrase/) | Generate Seedphrase | Create new BIP39 seed with wallet config |
| [set_passphrase](set_passphrase/) | Set Passphrase | Add BIP39 passphrase to seed |
| [manage_seedphrase](manage_seedphrase/) | Manage Seedphrase | View, backup, restore seed operations |
| [manage_device](manage_device/) | Manage Device | Device settings and configuration |
| [manage_firmware](manage_firmware/) | Manage Firmware | Firmware version and updates |
| [manage_security](manage_security/) | Security Features | PIN, self-test, duress settings |
| [interfaces](interfaces/) | Interfaces | Enable/disable QR, USB, SD, SmartCard |
| [manage_storage](manage_storage/) | Manage Storage | Internal flash and SmartCard management |
| [manage_backups](manage_backups/) | Manage Backups | SD card backup and restore |
| [locked](locked/) | Device Locked | PIN entry to unlock device |

## State-Dependent Screens

Some screens only appear when certain state conditions are met:
- `manage_wallet` - Requires active wallet
- `change_wallet` - Requires registered wallets
- `connect_sw_wallet` - Wallet connection flow
- `locked` - When device is locked
