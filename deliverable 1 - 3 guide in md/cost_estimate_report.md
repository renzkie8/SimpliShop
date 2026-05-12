# Deliverable 3: Cost Estimate Report - SimpliShop

## 1. Architecture Summary
The SimpliShop application is a cloud-native e-commerce platform deployed on Microsoft Azure. The architecture is designed for high availability and security, utilizing three distinct Azure services:
*   **Azure App Service**: Hosts the FastAPI backend and static frontend. Scaled to **2 instances** for high availability.
*   **Azure SQL Database**: Provides a secure, persistent relational database for user account management and authentication.
*   **GitHub Actions**: Implements a full CI/CD pipeline for automated testing and deployment.

## 2. Itemized Cost Breakdown (Monthly Estimate)
The following estimates are based on the Azure Pricing Calculator for the **Southeast Asia** region.

| Service | Configuration | Estimated Monthly Cost |
| :--- | :--- | :--- |
| **App Service Plan** | Basic (B1) - 2 Instances (High Availability) | ~$13.14 (per instance) |
| **Azure SQL Database** | Basic Tier (5 DTUs, 2GB Storage) | ~$4.90 |
| **Azure Storage** | Blob Storage (LRS) - ~1GB | ~$0.05 |
| **Bandwidth/Networking** | First 5GB free | $0.00 |
| **GitHub Actions** | Free for public repositories | $0.00 |
| **TOTAL** | | **~$31.23 USD** |

## 3. Cost Optimization Notes
To further reduce costs for the SimpliShop platform, we could implement the following:
*   **Reserved Instances**: By committing to a 1-year or 3-year term for the App Service plan, we could save up to 35% compared to pay-as-you-go pricing.
*   **Auto-scaling Rules**: Instead of keeping 2 instances running 24/7, we could use a Standard tier plan to automatically scale down to 1 instance during low-traffic hours and scale up only during peak shopping hours.
*   **Security & Secrets Management**: Utilizing Azure Key Vault (Standard Tier) would add ~0.03 to the monthly cost but provide hardware-backed security for all connection strings.
*   **Free Tier Database**: We are currently utilizing the "Azure SQL Database Free Offer" to eliminate database costs entirely during the initial implementation phase.

---

> [!IMPORTANT]
> **Azure Pricing Calculator Estimates**:
> ![Total Monthly Estimate](../screenshot%20of%20deliverables/screenshots/Deliverable%203%20SS/Total_Cost.png)
>
> **App Service Pricing Details**:
> ![App Service Cost](../screenshot%20of%20deliverables/screenshots/Deliverable%203%20SS/App_Service_Cost.png)
>
> **Azure SQL Pricing Details**:
> ![Azure SQL Cost](../screenshot%20of%20deliverables/screenshots/Deliverable%203%20SS/Azure-SQLDB_Cost.png)
