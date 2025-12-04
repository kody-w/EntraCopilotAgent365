"""
Environment Detection Utilities

Provides functions to detect the runtime environment (Azure vs Local)
and adjust behavior accordingly for optimal development experience.
"""

import os
import logging


def is_running_in_azure() -> bool:
    """
    Detect if the code is running in Azure (Functions or App Service).

    Azure environments set specific environment variables that we can check:
    - WEBSITE_INSTANCE_ID: Set by Azure App Service and Azure Functions
    - FUNCTIONS_WORKER_RUNTIME: Set by Azure Functions runtime
    - WEBSITE_SITE_NAME: Azure App Service site name

    Returns:
        bool: True if running in Azure, False if running locally
    """
    azure_indicators = [
        'WEBSITE_INSTANCE_ID',
        'FUNCTIONS_WORKER_RUNTIME',
        'WEBSITE_SITE_NAME',
        'APPSETTING_WEBSITE_SITE_NAME'  # Alternative variable name
    ]

    for indicator in azure_indicators:
        if os.environ.get(indicator):
            logging.info(f"Detected Azure environment via {indicator}")
            return True

    logging.info("Detected local development environment")
    return False


def should_use_azure_storage() -> bool:
    """
    Determine if Azure File Storage should be used.

    Returns True if:
    1. Running in Azure environment, OR
    2. All required Azure storage credentials are configured

    Returns:
        bool: True if Azure storage should be used, False for local fallback
    """
    # Always use Azure storage when running in Azure
    if is_running_in_azure():
        return True

    # For local development, only use Azure storage if fully configured
    storage_account = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
    share_name = os.environ.get('AZURE_FILES_SHARE_NAME')
    connection_string = os.environ.get('AzureWebJobsStorage', '')

    # Check if we have either connection string or managed identity setup
    has_connection_string = connection_string and 'AccountKey=' in connection_string
    has_token_auth = (
        os.environ.get('AZURE_TENANT_ID') and
        os.environ.get('AZURE_CLIENT_ID') and
        os.environ.get('AZURE_CLIENT_SECRET')
    )

    if storage_account and share_name and (has_connection_string or has_token_auth):
        logging.info("Azure storage fully configured for local development")
        return True

    logging.info("Azure storage not fully configured - will use local fallback")
    return False


def get_local_storage_path() -> str:
    """
    Get the path for local file storage fallback.

    Creates the directory if it doesn't exist.

    Returns:
        str: Absolute path to local storage directory
    """
    # Use .local_storage in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_storage = os.path.join(project_root, '.local_storage')

    # Create directory if it doesn't exist
    os.makedirs(local_storage, exist_ok=True)

    return local_storage
