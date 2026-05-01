# Changelog

## [12.8.8] - 2026-05-01

### Added
- **Stuck Game Watchdog**: Introduced a new mechanism to detect if the game is stuck. It automatically restarts the game and resumes the current task after a configurable period.
  - **How to enable**: Go to **Settings > Advanced** and enable "**Restart Stuck Tasks**".
  - **How it works**: You can set the inactivity period (in minutes) via the "**Restart Stuck Task After Mins**" setting.
- **Hero Recognition**: Added portrait recognition for new heroes: **Evie**, **Frieren**, and **Himmel**.
  - **Important Note**: Currently, only **Evie** has been fully tested and is confirmed working for AFK Stages. Frieren and Himmel are included but may require further optimization.
