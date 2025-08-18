# ASA Database - Azure Deployment

This document provides instructions for deploying the ASA Database application to Azure App Services with an Azure PostgreSQL database.

## Prerequisites

- Azure account with active subscription
- Azure CLI installed and logged in
- Git installed
- Python 3.8+

## Environment Variables

The following environment variables need to be set in Azure App Service:

- `DJANGO_SECRET_KEY`: A secure secret key for Django
- `DJANGO_DEBUG`: Set to 'False' for production
- `DJANGO_SETTINGS_MODULE`: Set to 'research_data_app.settings_azure'
- `POSTGRES_DATABASE`: Your Azure PostgreSQL database name
- `POSTGRES_USER`: Your Azure PostgreSQL username (format: username@server-name)
- `POSTGRES_PASSWORD`: Your Azure PostgreSQL password
- `POSTGRES_HOST`: Your Azure PostgreSQL host (format: server-name.postgres.database.azure.com)
- `POSTGRES_PORT`: Typically '5432'


{
  "charset": "UTF8",
  "collation": "en_US.utf8",
  "id": "/subscriptions/b80a476f-847b-4000-ad11-dc1c49603037/resourceGroups/asa_databases/providers/Microsoft.DBforPostgreSQL/flexibleServers/asa-databases-server/databases/lepidoptera-adults-db",
  "name": "lepidoptera-adults-db",
  "resourceGroup": "asa_databases",
  "systemData": null,
  "type": "Microsoft.DBforPostgreSQL/flexibleServers/databases"
}

## Deployment Steps

### 1. Create Azure Resources

```bash
# Log in to Azure CLI
az login

# Create a resource group
az group create --name asa-database-rg --location eastus

# Create an App Service Plan
az appservice plan create --name asa-database-plan --resource-group asa-database-rg --sku B1 --is-linux

# Create a PostgreSQL server
az postgres server create --resource-group asa-database-rg --name asa-database-server --admin-user azureuser --admin-password "ComplexPassword123!" --sku-name GP_Gen5_2

# Create a database
az postgres db create --resource-group asa-database-rg --server-name asa-database-server --name asadb

# Allow Azure services to access the PostgreSQL server
az postgres server firewall-rule create --resource-group asa-database-rg --server-name asa-database-server --name AllowAllWindowsAzureIps --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

# Create the Web App
az webapp create --resource-group asa-database-rg --plan asa-database-plan --name asa-database-app --runtime "PYTHON|3.10"
```

### 2. Configure App Service

```bash
# Set environment variables
az webapp config appsettings set --resource-group asa-database-rg --name asa-database-app --settings \
DJANGO_SECRET_KEY="your-secure-secret-key" \
DJANGO_DEBUG="False" \
DJANGO_SETTINGS_MODULE="research_data_app.settings_azure" \
POSTGRES_DATABASE="asadb" \
POSTGRES_USER="azureuser@asa-database-server" \
POSTGRES_PASSWORD="ComplexPassword123!" \
POSTGRES_HOST="asa-database-server.postgres.database.azure.com" \
POSTGRES_PORT="5432" \
SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# Configure startup command
az webapp config set --resource-group asa-database-rg --name asa-database-app --startup-file "startup.sh"
```

### 3. Deploy from GitHub

```bash
# Configure GitHub deployment
az webapp deployment source config --name asa-database-app --resource-group asa-database-rg --repo-url https://github.com/yourusername/ASA-Database.git --branch main --manual-integration
```

### 4. Manual Deployment (Alternative)

If you prefer to deploy manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Create a zip package
zip -r app.zip . -x "venv/*" ".git/*" ".gitignore" ".env"

# Deploy the zip package
az webapp deployment source config-zip --resource-group asa-database-rg --name asa-database-app --src app.zip
```

## Troubleshooting

- Check application logs: `az webapp log tail --name asa-database-app --resource-group asa-database-rg`
- SSH into App Service: `az webapp ssh --name asa-database-app --resource-group asa-database-rg`
- Check environment variables: Access the Azure Portal > App Service > Configuration > Application settings

## Local Development with Azure Database

1. Copy `.env.example` to `.env` and update with your Azure PostgreSQL credentials
2. Install dependencies: `pip install -r requirements.txt`
3. Run with Azure settings: `python manage.py runserver --settings=research_data_app.settings_azure`
