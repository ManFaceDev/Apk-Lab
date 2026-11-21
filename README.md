# APK Lab

Offline Android APK inspector with a dark interface. No root, account or internet permission required.

## Features in v0.1
- Pick local APK files using the Android document picker.
- Browse and extract ZIP entries, search paths and preview text/hex.
- Parse the binary Android manifest and list SDK levels, package name, permissions and components.
- Read DEX header statistics, detect native libraries and architecture directories.
- Compare the contents of two APKs using ZIP CRC and sizes.
- Calculate SHA-256 and export an analysis report.
- Detect some APK signing indicators **without cryptographically verifying signatures**.

**Not yet implemented:** HEX editing, manifest modifications, APK rebuilding/re-signing, JADX-style decompilation, APK Signature Scheme cryptographic verification, split APK reconstruction and ZIP64.

## Build

The current experimental Android WebView wrapper is built by `build_apk.py` using Python 3 and JDK (`keytool` and `jarsigner`). **No Android SDK is used.** The `assets/index.html` contains the offline interface and analysis logic.

```bash
python3 build_apk.py
```

GitHub Actions builds APKs on push and manual workflow dispatch. Find the APK under **Actions → latest successful Build APK Lab → Artifacts**. Without configured release signing secrets, CI signs with an **ephemeral development key** and its APK **cannot update existing installs or be used as a stable store release**.

### Set up production signing before publishing

Create and securely back up a permanent signing keystore **outside this repository**. Set GitHub Actions repository secrets:

- `APKLAB_RELEASE_KEYSTORE_B64` — base64-encoded entire keystore file (single line)
- `APKLAB_STORE_PASSWORD` — keystore password
- `APKLAB_KEY_ALIAS` — key alias
- `APKLAB_KEY_PASSWORD` — key password (optional if identical to store password)

Use the same signing key for every future store update. Never commit a keystore, password or unsigned release credentials to GitHub. A release should be tested and reviewed before uploading to an app store.

## Important limitations and store-readiness

- Android `minSdk=24`, `targetSdk=28`; the target SDK is **outdated for many Android stores**. Check target-SDK requirements with your chosen store and update the Android implementation before submission.
- Uses the old v1 JAR signature scheme; migrate to modern Android signing tooling for production.
- Uses an embedded WebView and `DecompressionStream('deflate-raw')`, so decompression requires a sufficiently recent Android System WebView.
- The project has been exercised in a Chromium browser but **not yet validated on a physical Android device**.
- ZIP64 and very large APKs may not work; SHA-256 currently reads the entire APK into memory.
- This is an early technical preview, not a finished APK editing toolkit.

## License

MIT — © 2026 ManFaceDev. See [LICENSE](LICENSE).