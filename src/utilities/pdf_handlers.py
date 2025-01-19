
import logging
import os
from pathlib import Path
from urllib.parse import urljoin
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

class DownloadError(Exception):
    """Custom exception for download-related errors."""
    pass


def download_pdf(
    reference: str,
    download_path: str | Path,
    base_url: str = "https://storage.googleapis.com/masteryhive-insurance-claims/rawtest/policy_document",
    chunk_size: int = 8192,
    timeout: int = 30
) -> tuple[bool, str]:
    """
    Download a PDF file from a cloud storage location.

    Args:
        reference (str): The reference identifier for the PDF file.
        download_path (str | Path): The directory path where the file should be downloaded.
        base_url (str, optional): The base URL for the storage location.
        chunk_size (int, optional): Size of chunks for streaming download. Defaults to 8192 bytes.
        timeout (int, optional): Request timeout in seconds. Defaults to 30.

    Returns:
        tuple[bool, str]: A tuple containing (success_status, message).
            success_status (bool): True if download was successful, False otherwise.
            message (str): Descriptive message about the operation result.

    Raises:
        DownloadError: If there are issues with the download process.
        ValueError: If the input parameters are invalid.
    """
    try:
        # Input validation
        if not reference or not download_path:
            raise ValueError("Reference and download path must not be empty")

        # Convert to Path object for better path handling
        download_dir = Path(download_path)
        modified_reference = reference.replace("/", "-")
        file_path = download_dir / f"{modified_reference}.pdf"

        # Create directory if it doesn't exist
        try:
            download_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise DownloadError(f"Permission denied creating directory: {download_dir}") from e

        # Check if file exists
        if file_path.exists():
            logger.info(f"File already exists: {file_path}")
            return True, "File already exists"

        # Construct URL and download file
        file_url = urljoin(base_url + "/", f"{modified_reference}.pdf")
        
        try:
            with requests.get(
                file_url,
                stream=True,
                timeout=timeout,
                headers={'User-Agent': 'PDF-Downloader/1.0'}
            ) as response:
                response.raise_for_status()
                
                # Get total file size for progress tracking
                total_size = int(response.headers.get('content-length', 0))
                
                # Download with progress tracking
                with open(file_path, 'wb') as f:
                    downloaded_size = 0
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # Log progress for larger files
                            if total_size > 1024*1024:  # 1MB
                                progress = (downloaded_size / total_size) * 100
                                logger.debug(f"Download progress: {progress:.1f}%")

                logger.info(f"Successfully downloaded file to {file_path}")
                return True, "File downloaded successfully"

        except requests.exceptions.HTTPError as e:
            raise DownloadError(f"HTTP error occurred: {e.response.status_code}") from e
        except requests.exceptions.ConnectionError as e:
            raise DownloadError("Network connection error occurred") from e
        except requests.exceptions.Timeout as e:
            raise DownloadError(f"Request timed out after {timeout} seconds") from e
        except requests.exceptions.RequestException as e:
            raise DownloadError(f"An error occurred while downloading: {str(e)}") from e

    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}", exc_info=True)
        return False, str(e)
    



def delete_pdf(reference: str, download_path: str) -> str:
    """
    Delete a PDF file from the specified path.
    
    Args:
        reference: The reference ID of the PDF file
        download_path: The directory path where the PDF is stored
        
    Returns:
        str: Status message indicating success or failure
    """
    modified_reference = reference.replace("/", "-")
    file_path = os.path.join(download_path, f"{modified_reference}.pdf")
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return "File deleted successfully"
        return "File does not exist"
    except Exception as e:
        return f"Error deleting file: {str(e)}"