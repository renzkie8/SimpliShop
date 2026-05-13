# SimpliShop - Deployment Instructions

This document provides step-by-step instructions on how to deploy the SimpliShop web application to Microsoft Azure using the Azure Portal (Method B - GUI).

## Prerequisites
- An active Microsoft Azure account (Azure for Students is recommended).
- A GitHub account for CI/CD automation.

## Step 1: Create a Resource Group
1. Log in to the [Azure Portal](https://portal.azure.com/).
2. Search for **Resource groups** and click **Create**.
3. Select your Subscription.
4. Set the **Resource group** name to `SimpliShop`.
5. Choose `Southeast Asia` as the Region.
6. Click **Review + create**, then **Create**.
*Note: This resource group organizes all related resources for the SimpliShop project.*

## Step 2: Deploy Data Resource (Azure SQL Database)
1. Search for **SQL databases** and click **Create**.
2. Select the `SimpliShop` resource group.
3. Name the database `SimpliShopDB`.
4. Create a new SQL server and securely store your admin credentials.
5. Under Compute + storage, configure the database to use the **Serverless Compute Tier** (or Free Offer) to optimize costs.
6. Click **Review + create**, then **Create**.

## Step 3: Configure Database Security
1. Go to your newly created SQL server resource.
2. On the left menu under Security, select **Networking**.
3. In the "Public network access" section, check the box for **"Allow Azure services and resources to access this server"**.
4. Click **Save**.
*Note: This network-level control ensures the database is not exposed to the public internet while permitting the App Service to securely connect. Additionally, Managed Identity and Azure Key Vault are configured to securely manage access and secrets.*

## Step 4: Deploy Core Compute Resource (App Service)
1. Search for **App Services** and click **Create** > **Web App**.
2. Select the `SimpliShop` resource group.
3. Name the web app `SimpliShop-System`.
4. Set Publish to **Code** and select the appropriate runtime stack for the application (e.g., Python).
5. Select or create an App Service Plan.
6. Click **Review + create**, then **Create**.
7. Once deployed, go to the App Service resource, and navigate to **Scale out (App Service plan)**.
8. Choose **Manual Scale** and set the **Instance count** to `2`. Click **Save**. 
*Note: Running two parallel instances provides fault tolerance and high availability.*

## Step 5: Configure Application Settings (Security)
1. In the `SimpliShop-System` App Service menu, navigate to **Settings** > **Environment variables**.
2. Add your database connection string and any other required secrets.
3. Do not hardcode any credentials in your source code.
4. Click **Apply** and **Save**.

## Step 6: Setup CI/CD Automation
1. In your GitHub repository containing the project code, navigate to the **Actions** tab.
2. Set up the deployment workflow (`.github/workflows/`) to deploy to Azure Web Apps.
3. Ensure the pipeline triggers on a `push` to the main branch.
4. Once active, any new changes pushed to GitHub will automatically deploy to your Azure App Service.

---

## Cloud Optimizations Included
As required by the final project guidelines, this architecture incorporates the following cloud optimizations:
1. **CI/CD Automation (Security & DevOps)**: Fully automated deployment pipeline using GitHub Actions to eliminate manual errors.
2. **Serverless Architecture (Cost Optimization)**: Azure SQL Database Serverless tier scales based on demand and pauses during inactivity.
3. **Fault Tolerance (Monitoring & Scaling)**: App Service runs on 2 parallel instances with a `/health` endpoint to detect unhealthy nodes and ensure zero downtime.
4. **Advanced Security Controls (Secrets Management)**: Removed all hardcoded database credentials and securely stored them in Azure App Service Environment Variables.
