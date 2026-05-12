# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2026-05-12] - Milestone: Azure SQL Integration & High Availability
### Added
- [Carl Renz M. Colico & Francis Gabriel Nonato] - Provisioned Azure SQL Database (Basic Tier) and Logical Server.
- [Carl Renz M. Colico & Francis Gabriel Nonato] - Implemented backend API endpoints for User Registration and Authentication.
- [ Francis Gabriel Nonato] - Created the `Users` database schema for persistent cloud storage.
- [Carl Renz M. Colico & Francis Gabriel Nonato] - Configured App Service "Scale Out" to 2 instances for High Availability (Optimization 2).
- [ Francis Gabriel Nonato] - Established professional repository structure (`/diagram`, `/deployment`, `/report`).

### Changed
- [Carl Renz M. Colico ] - Migrated project from Pharmacy Management System to SimpliShop (Static Web App).
- [ Francis Gabriel Nonato] - Created Azure App Service `SimpliShop-System` on Python 3.11 runtime.
- [Carl Renz M. Colico ] - Implemented FastAPI `app.py` to serve static content and database APIs.
- [Carl Renz M. Colico & Francis Gabriel Nonato] - Established GitHub Actions CI/CD pipeline (Optimization 1).
- [ Francis Gabriel Nonato] - Updated frontend JavaScript to utilize real-time Fetch API calls to Azure SQL.

### Fixed
- [Carl Renz M. Colico & Francis Gabriel Nonato] - Resolved "Invalid object name 'Users'" error by implementing robust table initialization logic.
- [Carl Renz M. Colico & Francis Gabriel Nonato] - Resolved "Internal Server Error" by adding explicit startup command in Azure Configuration.
