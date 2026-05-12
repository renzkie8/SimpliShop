# Deliverable 2: Deployment Documentation (Method B - GUI)

## 1. Resource Group
*   **Resource**: `SimpliShop`
*   **Screenshot 1**: Show the Overview of the `SimpliShop` resource group.
*   **Explanation**: This container organizes all related resources for the SimpliShop project, allowing for unified billing and security management in the Southeast Asia region.

## 2. Core Compute Resource
*   **Resource**: `SimpliShop-System` (App Service)
*   **Screenshot 2**: Show the **Scale out (App Service plan)** settings.
*   **Requirement**: Must show **Manual Scale** with **Instance count = 2**.
*   **Explanation**: High availability is achieved by running two parallel instances of the web application. This ensures that the platform remains accessible even if one underlying server node experiences maintenance or failure.

## 3. Data Resource
*   **Resource**: `SimpliShopDB` (Azure SQL Database)
*   **Screenshot 3**: Show the **Database Overview** or the **Query Editor** with a successful login.
*   **Explanation**: Azure SQL provides a secure, managed relational database. We utilized the "Free Offer" tier to store user credentials for the authentication module.

## 4. Security Control
*   **Resource**: SQL Firewall / App Service Authentication
*   **Screenshot 4**: Show the **Networking** tab of the SQL Server.
*   **Screenshot 5**: Show the **Identity** tab of the App Service Server. Other to add is Key vault
*   **Requirement**: Highlight the checkbox "Allow Azure services and resources to access this server."
*   **Explanation**: This network-level security control ensures that the database is not exposed to the public internet, while explicitly permitting the App Service to establish a secure connection.

## 5. Optimization (CI/CD)
*   **Resource**: GitHub Actions
*   **Screenshot 6**: Show a "Green" success bar from the **Actions** tab in GitHub.
*   **Explanation**: Automation via GitHub Actions ensures that every code change is automatically deployed to Azure, maintaining a consistent and professional release cycle.
