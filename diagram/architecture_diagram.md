# Architecture Diagram: SimpliShop Cloud Deployment

This diagram illustrates the "Cloud Optimized" architecture for the SimpliShop e-commerce platform on Microsoft Azure.

```mermaid
graph TD
    subgraph "Local Development"
        Dev[Developer]
        Git[Git Repo]
    end

    subgraph "CI/CD Pipeline (GitHub)"
        GHA[GitHub Actions]
    end

    subgraph "Azure Cloud Platform"
        subgraph "Web Layer"
            WebApp[Azure App Service<br/>SimpliShop-System]
            Inst1[Instance 1]
            Inst2[Instance 2]
        end

        subgraph "Data & Storage Layer"
            SQL[Azure SQL Database<br/>SimpliShopDB]
            Storage[Azure Blob Storage<br/>Static Assets/Images]
        end

        subgraph "Security"
            Env[Managed Environment Variables]
        end
    end

    Dev -->|Push Code| Git
    Git -->|Trigger| GHA
    GHA -->|Deploy via OIDC| WebApp
    WebApp --> Inst1
    WebApp --> Inst2
    Inst1 -->|Query| SQL
    Inst2 -->|Query| SQL
    Inst1 -->|Retrieve| Storage
    Inst2 -->|Retrieve| Storage
    Env -->|Provide Secrets| Inst1
    Env -->|Provide Secrets| Inst2
    
    User[End User] -->|HTTPS Request| WebApp
```

## Key Architectural Principles Applied:
1.  **Separation of Concerns**: Static assets are offloaded to Azure Storage, while logic is handled by App Service.
2.  **High Availability**: Deployed across multiple instances (Scale-out).
3.  **Security by Design**: Credentials are never stored in code; they are managed via Azure App Service configuration.
4.  **Automation**: Full CI/CD lifecycle using GitHub Actions.
