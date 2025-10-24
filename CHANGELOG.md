# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `strip_merge_markers` helper removes ``DO_NOT_MERGE_MARKER`` keys and emits
	a warning listing JSONPath-style locations.
- `hydrate` now accepts a `strip_merge_markers` flag to apply the helper
	automatically after hydration.

## [0.1.2] - 2024-12-03

### Fixed

- Allow `None` for base ([#8](https://github.com/developmentseed/hydraters/pull/8))

## [0.1.1] - 2024-11-15

### Added

- Dehydration ([#2](https://github.com/developmentseed/hydraters/pull/2))
- Docs ([#4](https://github.com/developmentseed/hydraters/pull/4))

### Changed

- Moved to <https://github.com/developmentseed/hydraters>

## [0.1.0] - 2024-11-11

Initial release

[Unreleased]: https://github.com/developmentseed/hydraters/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/developmentseed/hydraters/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/developmentseed/hydraters/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/developmentseed/hydraters/releases/tag/v0.1.0
