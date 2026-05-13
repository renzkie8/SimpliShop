# SimpliShop - Cloud E-Commerce Deployment

**Course**: CSEC 3 – Cloud Computing  
**Team**: Carl Renz M. Colico & Francis Gabriel Nonato  
**Live Demo**: [https://simplishop-system-e5gedhdsbacjbmcn.southeastasia-01.azurewebsites.net](https://simplishop-system-e5gedhdsbacjbmcn.southeastasia-01.azurewebsites.net)  
**Video Presentation**: [YouTube Link Placeholder]  

---

## Project Overview

SimpliShop is a professional, cloud-native e-commerce platform developed for our final project. It has been fully migrated from a local environment to a robust Microsoft Azure architecture, utilizing FastAPI for the backend and a real Azure SQL Database for persistent user authentication.

### Core Cloud Features
- **User Authentication (Azure SQL)**: Unlike local prototypes, SimpliShop now uses a real Azure SQL Database. You can "Create an Account" on the Sign-Up page, and your data will be securely stored in the cloud.
- **High Availability**: The platform is scaled to multiple instances on Azure, ensuring that the website remains fast and accessible at all times.
- **CI/CD Integration**: Any updates to the system are automatically deployed via GitHub Actions, following professional DevOps practices.

### Key Functional Workflows
- **Real Sign-Up/Login**: Test the system by creating a new account. Your credentials will be verified against our live SQL Server.
- **Dynamic Search**: Use the search bar to find products (headphones, smartphones, etc.) with real-time suggestions.
- **Product Comparison**: Select multiple products to see a side-by-side comparison in a modal window.
- **Full Checkout Flow**: Add items to your cart and follow the professional checkout process from shipping to payment confirmation.

---

## Cloud Architecture & Technology

- **Cloud Provider**: Microsoft Azure
- **Compute**: Azure App Service (Python 3.11 / FastAPI)
- **Database**: Azure SQL Database (Basic Tier)
- **Optimization 1**: GitHub Actions CI/CD Pipeline
- **Optimization 2**: Scale-Out (High Availability)

---

## Repository Structure

```text
/
├── .github/workflows/          # CI/CD: Automated deployment pipeline to Azure
├── deployment/
│   ├── screenshots/            # GUI: Folder containing all Azure Portal screenshots
│   └── README.md               # Clear step-by-step deployment instructions
├── diagram/
│   └── architecture.png        # Architecture diagram mapping out the Azure components
├── report/
│   └── cost-estimate.md        # Cost estimate report and Azure Pricing Calculator results
├── app.py                      # Core application backend (FastAPI)
├── (HTML/CSS/JS files)         # Application frontend templates and static assets
├── CHANGELOG.md                # Detailed chronological log of all project updates and team contributions
└── README.md                   # Project overview, team members, video link, and demo URL
```


---

## Screenshots & Deliverables

### Deliverable 2 - Deployment Documentation - Method B (GUI)

| Resource & Screenshot | Description |
| --- | --- |
| **Activity Log (Database)**<br>![Activity Log Database](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/Activity-Log_DB_SimpliShop.png) | Shows the creation and recent deployment operations of our Azure SQL Database. |
| **Activity Log (System)**<br>![Activity Log System](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/Activity-Log_SimpliShop.png) | An overview of all deployment activities and updates within the main resource group. |
| **App Service Plan (Scale Out)**<br>![App Service Plan](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/AppServicePlan_SimpliShop.png) | Displays the App Service being scaled out manually to multiple instances for high availability and fault tolerance. |
| **Azure SQL Database Overview**<br>![Azure SQL Database Overview](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/AzureSQLDB_Overview_SimpliShop.png) | The configuration and overview page of the deployed serverless SQL Database. |
| **CI/CD Pipeline**<br>![CI/CD Pipeline](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/CICD_SimpliShop.png) | Evidence of our GitHub Actions workflow successfully building and deploying our web application directly to Azure. |
| **Database Storage Account**<br>![Database Storage Account](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/DB-StorageAcc_SimpliShop.png) | The storage account provisioned for database auditing and log backups. |
| **Azure Key Vault**<br>![Azure Key Vault](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/KeyVault_SimpliShop.png) | Securely stores and manages application secrets and database credentials to prevent exposure. |
| **Managed Identity**<br>![Managed Identity](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/Managed-Identity_SimpliShop.png) | System-assigned managed identity used to securely authenticate Azure services together without using hardcoded credentials. |
| **Network Security Group (NSG)**<br>![Network Security Group](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/NSG_SimpliShop.png) | Demonstrates the security rules regulating inbound and outbound network traffic to protect the infrastructure. |
| **SQL Server Networking**<br>![SQL Server Networking](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/Networking_SQL-Server_SimpliShop.png) | Firewall rules carefully configured to allow secure access only from permitted Azure resources and services. |
| **Resource Group Overview**<br>![Resource Group Overview](deployment/screenshots/Deliverable%202%20-%20Deployment%20Documentation%20-%20Method%20B%20(GUI)/Overview_SimpliShop.png) | The central SimpliShop Resource Group containing all of our provisioned Azure components. |

<br>

### Deliverable 3 - Cost Estimate Report

| Resource & Screenshot | Description |
| --- | --- |
| **App Service Cost Estimate**<br>![App Service Cost](deployment/screenshots/Deliverable%203%20-%20Cost%20Estimate%20Report/App_Service_Cost.png) | The calculated monthly estimated cost for running our App Service compute instances using the Azure Pricing Calculator. |
| **Azure SQL Database Cost Estimate**<br>![Azure SQL Database Cost](deployment/screenshots/Deliverable%203%20-%20Cost%20Estimate%20Report/Azure-SQLDB_Cost.png) | Projected monthly costs for our Basic/Serverless SQL Database tier to ensure an optimized budget. |
| **Total Architecture Cost**<br>![Total Architecture Cost](deployment/screenshots/Deliverable%203%20-%20Cost%20Estimate%20Report/Total_Cost.png) | The comprehensive overall monthly budget estimate for the entire SimpliShop Azure deployment. |
