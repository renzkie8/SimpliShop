# SimpliShop - Cloud E-Commerce Deployment
**Course**: CSEC 3 – Cloud Computing  
**Team**: Carl Renz M. Colico & Francis Gabriel Nonato
**Live Demo**: [https://simplishop-system.azurewebsites.net](https://simplishop-system.azurewebsites.net)  
**Video Presentation**: [YouTube Link Placeholder]

## 1. Project Overview
SimpliShop is a clean and organized e-commerce website deployed on Microsoft Azure. This project demonstrates basic cloud architecture principles, focusing on high availability, scalability, and automated CI/CD pipelines.

## 2. Cloud Architecture & Optimization
Our deployment features a "Cloud Optimized" architecture with the following improvements over a baseline deployment:
1. **CI/CD Pipeline (Optimization 1)**: Automated deployment from GitHub to Azure App Service using GitHub Actions and OpenID Connect (OIDC).
2. **Scalability (Optimization 2)**: Configured App Service to run on 2+ instances with manual scale-out for high availability.
3. **Security & Secrets (Optimization 3)**: Migrated hardcoded database credentials to Azure App Service Environment Variables (Managed Secrets) to prevent sensitive data exposure in the repository.
4. **Blob Storage Offloading (Optimization 4)**: Offloaded static assets and product images to Azure Storage to reduce web server load and improve performance.

## 3. Azure Services Used (Minimum 3)
1. **Azure App Service**: Hosts the FastAPI web server and static frontend.
2. **Azure SQL Database**: Provides persistent storage for user accounts and orders.
3. **Azure Storage (Blob)**: Used for storing product images and static assets to ensure low-latency delivery.

## 4. Repository Structure
- `/diagram/`: Architecture diagrams (Baseline vs. Improved).
- `/deployment/`: Step-by-step deployment documentation and screenshots.
- `/report/`: Cost estimate report and Azure Pricing Calculator results.
- `CHANGELOG.md`: Detailed log of all project updates.
