# Madeira iPad test build

This repository runs the public Madeira build contribution on a GitHub-hosted Apple Silicon Mac, so a local Mac is not required to create the IPA.

- Upstream project: https://github.com/willfaust/Madeira
- Build contribution: https://github.com/willfaust/Madeira/pull/14
- Pinned source: https://github.com/JMRBDev/Madeira/tree/ef496822ca427b4b000eaf7c78d3a570e23182e1
- Build history: https://github.com/rtyuia123/madeira-ipad-build/actions/workflows/madeira-ios.yml

On a successful run, download the `Madeira-iPad-IPA` artifact. It contains the IPA, its SHA-256 checksum, and source information. Failed runs retain `Madeira-build-logs` for diagnosis. Artifacts expire after seven days.

The build targets iPadOS 18.0 or later. The IPA needs personal development signing through a compatible sideloading tool, followed by JIT activation. This workflow uses no Apple account, signing certificate, or game files.

A successful package build does not establish successful installation or game compatibility. On-device testing is tracked separately. The upstream project and its components retain their respective licenses; see the pinned source and its notices.

## Verified package

[Build 8](https://github.com/rtyuia123/madeira-ipad-build/actions/runs/36168732574) completed successfully. The IPA is 57,208,156 bytes and has SHA-256 `232c62c490fd5e05bfb08595da1e23a49c6b61e7efc542975ae6a9383e9bd4d1`.

Archive integrity, ARM64 Mach-O architecture, iPad device support, required runtime resources, and bundled clock/cube test programs were checked. Installation, JIT execution, and gameplay have not yet been tested on a device.

The workflow applies compatibility fixes for iOS diagnostics, required static-library targets, LLVM Apple linker options, older-SDK SwiftUI fallbacks, and recursive extraction of explicitly labelled AMD64 Microsoft runtime payloads. Build patches and runtime checksums are retained in the diagnostic logs.
