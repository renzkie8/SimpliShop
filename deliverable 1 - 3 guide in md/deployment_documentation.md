# Deliverable 2: Deployment Documentation (Method B - GUI)

## 1. Resource Group
*   **Resource**: `SimpliShop`
*   **Screenshot 1**: ![Resource Group Overview](../screenshot%20of%20deliverables/screenshots/Delivarable%202%20SS/Overview_SimpliShop.png)
*   **Explanation**: This container organizes all related resources for the SimpliShop project, allowing for unified billing and security management in the Southeast Asia region.

## 2. Core Compute Resource
*   **Resource**: `SimpliShop-System` (App Service)
*   **Screenshot 2**: ![Scale Out Settings](../screenshot%20of%20deliverables/screenshots/Delivarable%202%20SS/AppServicePlan_SimpliShop.png)
*   **Requirement**: Must show **Manual Scale** with **Instance count = 2**.
*   **Explanation**: High availability is achieved by running two parallel instances of the web application. This ensures that the platform remains accessible even if one underlying server node experiences maintenance or failure.

## 3. Data Resource
*   **Resource**: `SimpliShopDB` (Azure SQL Database)
*   **Screenshot 3**: ![Azure SQL Database Overview](../screenshot%20of%20deliverables/screenshots/Delivarable%202%20SS/AzureSQLDB_Overview_SimpliShop.png)
*   **Explanation**: Azure SQL provides a secure, managed relational database. We utilized the "Free Offer" tier to store user credentials for the authentication module.

## 4. Security Control
*   **Resource**: SQL Firewall / App Service Authentication
*   **Screenshot 4**: ![SQL Server Networking](../screenshot%20of%20deliverables/screenshots/Delivarable%202%20SS/Networking_SQL-Server_SimpliShop.png)
*   **Screenshot 5**: ![Managed Identity](../screenshot%20of%20deliverables/screenshots/Delivarable%202%20SS/Managed-Identity_SimpliShop.png)
*   **Additional Security (Key Vault)**: ![Azure Key Vault](../screenshot%20of%20deliverables/screenshots/Delivarable%202%20SS/KeyVault_SimpliShop.png)
*   **Requirement**: Highlight the checkbox "Allow Azure services and resources to access this server."
*   **Explanation**: This network-level security control ensures that the database is not exposed to the public internet, while explicitly permitting the App Service to establish a secure connection.

## 5. Optimization (CI/CD)
*   **Resource**: GitHub Actions
*   **Screenshot 6**: ![GitHub Actions Success](../screenshot%20of%20deliverables/screenshots/Delivarable%202%20SS/CICD_SimpliShop.png)
*   **Explanation**: Automation via GitHub Actions ensures that every code change is automatically deployed to Azure, maintaining a consistent and professional release cycle.
