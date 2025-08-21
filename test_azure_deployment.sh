#!/bin/bash
# test_azure_deployment.sh
# Script to test Azure deployment configuration locally

echo "===== TESTING AZURE DEPLOYMENT CONFIGURATION ====="
echo "This script simulates the environment in Azure App Service"

# Create a test directory to simulate Azure's extraction behavior
TEST_DIR="/tmp/azure_test_$(date +%s)"
echo "Creating test directory: $TEST_DIR"
mkdir -p "$TEST_DIR"

# Copy all necessary files to the test directory
echo "Copying application files to test directory..."
cp -r ./* "$TEST_DIR/"

# Set environment variables similar to Azure
echo "Setting up environment variables..."
export DJANGO_SETTINGS_MODULE=research_data_app.settings_azure
export POSTGRES_DATABASE=${POSTGRES_DATABASE:-"testdb"}
export POSTGRES_USER=${POSTGRES_USER:-"testuser"}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"testpassword"}
export POSTGRES_HOST=${POSTGRES_HOST:-"localhost"}
export DJANGO_ADMIN_PASSWORD=${DJANGO_ADMIN_PASSWORD:-"testadmin"}
export WEBSITE_HOSTNAME="localhost"

# Change to the test directory
echo "Changing to test directory..."
cd "$TEST_DIR"

# Run the startup script
echo "Running startup script in test environment..."
bash ./startup.sh

# Clean up
echo "Test complete. Clean up test directory? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Cleaning up test directory..."
    rm -rf "$TEST_DIR"
else
    echo "Test directory not removed: $TEST_DIR"
fi

echo "===== TEST COMPLETE ====="
