# Changelog

## [12.8.8] - 2026-05-01

### Added
- **Hero Recognition**: Added and optimized Evie portrait recognition for AFK Stages.
- **Testing Suite**: Added 24 new unit tests covering core automation logic:
  - `tests/utils/test_execute_restart.py`: Watchdog and auto-restart logic.
  - `tests/games/afk_journey/test_navigation_extended.py`: Navigation handling for various game states (World, Homestead, Arcane Labyrinth, etc.).
  - `tests/games/afk_journey/test_afkj_base_coverage.py`: Hero exclusion and battle start logic.
- **Utility Scripts**: Added `template_optimizer.py` and `hero_template_extractor.py` in `scratch/` (added to `.gitignore`) for easier hero recognition maintenance.

### Changed
- **Automation Core**: Refactored `Execute` class to support instance-bound methods in `find_command_and_execute`, enabling proper watchdog functionality for game-specific commands.
- **Project Version**: Incremented version to 12.8.8 across all configuration files (`tauri.conf.json`, `package.json`, `Cargo.toml`).

### Fixed
- **Watchdog Logic**: Resolved an issue where the game restart timer was not triggered for instance methods.
- **Testing**: Fixed 2 failing unit tests in `test_execute.py` by correcting assertion values for `find_command_and_execute`.
- **Linting**: Fixed various linting issues in tests and scratch scripts to comply with project standards and pass pre-commit hooks.
