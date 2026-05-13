# Changelog

All notable changes to this project will be documented in this file.

## [2026-05-13] - Final Project Documentation & Cleanup

### Added
- `[Francis Gabriel F. Nonato]` - Created detailed `README.md` in the `/deployment` folder with step-by-step GUI deployment instructions.

### Changed
- `[Francis Gabriel F. Nonato]` - Updated the root `README.md` to integrate project overview, cloud architecture, and live URLs.
- `[Francis Gabriel F. Nonato]` - Reformatted the `README.md` screenshots section into a professional markdown table with descriptions.
- `[Francis Gabriel F. Nonato]` - Updated the repository structure section in `README.md` to display as an ASCII folder tree.
- `[Francis Gabriel F. Nonato]` - Standardized `CHANGELOG.md` formatting and author tags to strictly conform to project rubrics.

### Fixed
- No bug fixes for this documentation milestone.

### Removed
- `[Francis Gabriel F. Nonato]` - Deleted `deployment_documentation.md` and `CLOUD_OPTIMIZATIONS_Requirements.md` after migrating their content.
- `[Francis Gabriel F. Nonato]` - Deleted `TEAM_TASKS.md` and `HOW TO RUN.txt` reference files to finalize the repository structure for submission.

---

## [2026-05-12] - Milestone: Azure SQL Integration & High Availability

### Added
- `[Carl Renz M. Colico & Francis Gabriel F. Nonato]` - Provisioned Azure SQL Database (Basic Tier) and Logical Server.
- `[Carl Renz M. Colico & Francis Gabriel F. Nonato]` - Implemented backend API endpoints for User Registration and Authentication.
- `[Francis Gabriel F. Nonato]` - Created the `Users` database schema for persistent cloud storage.
- `[Carl Renz M. Colico & Francis Gabriel F. Nonato]` - Configured App Service "Scale Out" to 2 instances for High Availability (Optimization 2).
- `[Francis Gabriel F. Nonato]` - Established professional repository structure (`/diagram`, `/deployment`, `/report`).
- `[Carl Renz M. Colico]` - Implemented Security Optimization 3: Migrated credentials to environment variables.
- `[Carl Renz M. Colico]` - Added `/health` monitoring endpoint for Azure App Service observability.

### Changed
- `[Francis Gabriel F. Nonato]` - Migrated project from Pharmacy Management System to SimpliShop (Static Web App).
- `[Francis Gabriel F. Nonato]` - Created Azure App Service `SimpliShop-System` on Python 3.11 runtime.
- `[Carl Renz M. Colico]` - Implemented FastAPI `app.py` to serve static content and database APIs.
- `[Carl Renz M. Colico]` - Established GitHub Actions CI/CD pipeline.
- `[Francis Gabriel F. Nonato]` - Updated frontend JavaScript to utilize real-time Fetch API calls to Azure SQL.

### Fixed
- `[Carl Renz M. Colico & Francis Gabriel F. Nonato]` - Resolved "Invalid object name 'Users'" error by implementing robust table initialization logic.
- `[Carl Renz M. Colico & Francis Gabriel F. Nonato]` - Resolved "Internal Server Error" by adding explicit startup command in Azure Configuration.

### Removed
- No removed resources for this milestone.
