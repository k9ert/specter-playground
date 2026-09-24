# Documentation

Setup and build are described in the [main README](../README.md).

Different scenarios can be simulated like:

```
# Default - runs the MockUI (scenarios/mockui_fw/main.py)
nix develop -c make simulate

# Run address_navigator
nix develop -c make simulate SCRIPT=address_navigator.py

# Run udisplay_demo
nix develop -c make simulate SCRIPT=udisplay_demo.py
```

Feel free to contribute! I'll probably merge your PRs without (much) review.

## Developer Tools

- [RAG Code Scanner](rag-setup.md) - Local semantic search over the codebase with Claude Code MCP integration
- [MockUI Control Contract](../devtools/docs/control-contract.md) - Run the same UI operation on the simulator or hardware (devtools submodule)
