# Changelog

## v0.3.1 – 2025-04-27

### Fixed

- Stripping numbers for fuzzy matching did not work properly (introduced in v0.3.0)

## v0.3.0 – 2025-04-26

### Improved

- Test suite
- GitHub Actions for linting and testing

## v0.2.0 – 2025-04-26

### Added

- Support for optional Pushover `title` parameter in the configuration
- Support for mapping journald priorities to Pushover priorities via `priority-map` configuration

### Improved

- Docs
- Pre-compiled regular expressions for better performance
- Error handling for network requests

### Fixed

- Renamed `deduplication-timeout` to `deduplication-window` in config example to match code

## v0.1.0 – 2024-02-13

- Initial release
