# Changelog

## [12.9.28] - 2026-08-11

### Bug Fixes

- **Device Streaming**: Fixed emulator detection false-positives on Google Tensor Pixel phones (6/7/8/9 series), whose Samsung modem firmware string was misread as an emulator marker, silently blocking Device Streaming on macOS and degrading capture on other platforms.
- **Profiles**: Fixed deleting a profile leaving its settings folder behind instead of cleaning it up, which could cause a later profile to silently read/write another profile's settings.
- **Profiles**: Fixed a cache-clearing bug where saving settings for profile 0 could clear cached state for other profiles too.
