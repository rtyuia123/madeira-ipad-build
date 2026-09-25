# Madeira iPad test build

This repository runs the public Madeira build contribution on a GitHub-hosted Apple Silicon Mac, so a local Mac is not required to create the IPA.

- Upstream project: https://github.com/willfaust/Madeira
- Build contribution: https://github.com/willfaust/Madeira/pull/14
- Pinned source: https://github.com/JMRBDev/Madeira/tree/ef496822ca427b4b000eaf7c78d3a570e23182e1
- Build history: https://github.com/rtyuia123/madeira-ipad-build/actions/workflows/madeira-ios.yml

On a successful run, download the `Madeira-iPad-IPA` artifact. It contains the IPA, its SHA-256 checksum, and source information. Failed runs retain `Madeira-build-logs` for diagnosis. Artifacts expire after seven days.

The build targets iPadOS 18.0 or later. The IPA needs personal development signing through a compatible sideloading tool, followed by JIT activation. This workflow uses no Apple account, signing certificate, or game files.

A successful package build does not establish successful installation or game compatibility. On-device testing is tracked separately. The upstream project and its components retain their respective licenses; see the pinned source and its notices.
