"""
Storage Factory

Provides a factory function to get the appropriate storage manager
based on the environment (Azure vs Local).
"""

import logging
from typing import Union

from utils.environment import should_use_azure_storage, is_running_in_azure
from utils.local_file_storage import LocalFileStorageManager


def get_storage_manager() -> Union['AzureFileStorageManager', LocalFileStorageManager]:
    """
    Get the appropriate storage manager based on environment.

    Returns:
        AzureFileStorageManager if in Azure or fully configured for local dev,
        LocalFileStorageManager as fallback for local development.
    """
    if should_use_azure_storage():
        try:
            # Import here to avoid issues if Azure SDK not available
            from utils.azure_file_storage import AzureFileStorageManager

            logging.info("Using Azure File Storage")
            return AzureFileStorageManager()

        except Exception as e:
            logging.warning(f"Failed to initialize Azure File Storage: {str(e)}")

            # If running in Azure, this is a critical error
            if is_running_in_azure():
                logging.error("CRITICAL: Azure storage failed in Azure environment!")
                raise

            # For local development, fall back gracefully
            logging.info("Falling back to local file storage for development")
            return LocalFileStorageManager()
    else:
        logging.info("Using local file storage for development")
        return LocalFileStorageManager()


def create_storage_manager_safe() -> Union['AzureFileStorageManager', LocalFileStorageManager, None]:
    """
    Safely create a storage manager, returning None if all methods fail.

    Use this when storage is truly optional (e.g., for caching).

    Returns:
        Storage manager instance or None if initialization fails
    """
    try:
        return get_storage_manager()
    except Exception as e:
        logging.error(f"Failed to create any storage manager: {str(e)}")
        return None
