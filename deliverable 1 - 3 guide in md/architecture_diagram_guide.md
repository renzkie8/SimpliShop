# Deliverable 1: Architecture Diagram Guide - SimpliShop

This document describes the architecture of the SimpliShop system. You should use this to create your visual diagram in **draw.io** or **Canva**.

## 1. Visual Components (The "Boxes")

### A. The User (Client Side)
*   **Icon**: Laptop/Mobile User.
*   **Protocol**: HTTPS (Port 443).

### B. Security & Optimization Boundary
*   **GitHub Actions (CI/CD)**: Represents the automated deployment pipeline.
*   **Identity (Managed Identity/OIDC)**: Secure connection between GitHub and Azure.

### C. Azure App Service (Compute Layer)
*   **Icon**: Azure App Service icon.
*   **Highlight**: Draw **two** small server icons inside to represent the **2 instances** (High Availability/Optimization).
*   **Environment**: Python 3.11 / FastAPI.

### D. Azure SQL Database (Data Layer)
*   **Icon**: Azure SQL Database icon.
*   **Connection**: Arrow from App Service to SQL Database.
*   **Protocol**: SQL Authentication (Encrypted connection).

## 2. Connections & Flows

1.  **Code Flow**: Developer → GitHub → GitHub Actions → Azure App Service.
2.  **User Flow**: User → HTTPS → Azure App Service (Instance 1 & 2).
3.  **Data Flow**: App Service → SQL Query → Azure SQL Database.

## 3. Optimizations to Highlight
*   **High Availability**: Scale-out to 2 instances ensures service continuity.
*   **CI/CD**: Automated deployment via GitHub Actions reduces human error.
*   **Security Firewall**: SQL Database firewall restricted to "Allow Azure Services" only.

---

### Suggested Tool:
Use [draw.io](https://app.diagrams.net/) and search for "Azure" in the shape library to find professional icons for:
*   `App Services`
*   `SQL Database`
*   `GitHub`
