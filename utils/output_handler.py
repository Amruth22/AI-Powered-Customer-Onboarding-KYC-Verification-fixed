import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


def save_complete_output(result: Any, filename: str = "kyc_analysis_complete.json") -> bool:
    """
    Save the complete output to a JSON file.

    Args:
        result: The result from crew execution
        filename: Name of the output file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs("outputs", exist_ok=True)

        output_path = os.path.join("outputs", filename)

        # Convert result to JSON-serializable format
        if isinstance(result, dict):
            output_data = result
        else:
            output_data = {"result": str(result), "timestamp": datetime.now().isoformat()}

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, default=str)

        logger.info(f"Complete output saved to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving complete output: {e}")
        return False


def save_metadata_output(metadata_list: list, filename: str = "file_metadata.json") -> bool:
    """
    Save file metadata to a separate JSON file.

    Args:
        metadata_list: List of file metadata dictionaries
        filename: Name of the output file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs("outputs", exist_ok=True)

        output_path = os.path.join("outputs", filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata_list, f, indent=2, default=str)

        logger.info(f"Metadata saved to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving metadata: {e}")
        return False


def save_kyc_analysis(analysis_result: Dict[str, Any], filename: str = "kyc_analysis_results.json") -> bool:
    """
    Save KYC analysis results to a JSON file.

    Args:
        analysis_result: Dictionary containing KYC analysis results
        filename: Name of the output file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs("outputs", exist_ok=True)

        output_path = os.path.join("outputs", filename)

        # Add timestamp to the analysis
        analysis_result['generated_at'] = datetime.now().isoformat()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2, default=str)

        logger.info(f"KYC analysis saved to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving KYC analysis: {e}")
        return False


def process_and_save_results(result: Any) -> bool:
    """
    Process crew execution results and save all outputs.

    This is a convenience function that combines saving different types of outputs.

    Args:
        result: The result from crew execution

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not save_complete_output(result):
            logger.error("Failed to save complete output")
            return False

        # If result is a dictionary with specific keys, save them separately
        if isinstance(result, dict):
            if 'file_metadata' in result:
                save_metadata_output(result['file_metadata'])

            if 'document_processing_results' in result:
                save_kyc_analysis(result)

        logger.info("All results processed and saved successfully")
        return True

    except Exception as e:
        logger.error(f"Error processing and saving results: {e}")
        return False


def create_output_summary(result: Dict[str, Any]) -> str:
    """
    Create a human-readable summary of the processing results.

    Args:
        result: Dictionary containing processing results

    Returns:
        str: Formatted summary text
    """
    summary = []
    summary.append("=" * 70)
    summary.append("KYC VERIFICATION PROCESSING SUMMARY")
    summary.append("=" * 70)

    if 'package_id' in result:
        summary.append(f"\nPackage ID: {result['package_id']}")

    if 'total_files' in result:
        summary.append(f"Total Files Processed: {result['total_files']}")

    if 'file_categories' in result:
        categories = result['file_categories']
        summary.append(f"\nFile Categories:")
        summary.append(f"  - Documents: {categories.get('documents', 0)}")
        summary.append(f"  - Images: {categories.get('images', 0)}")
        summary.append(f"  - Other: {categories.get('other', 0)}")

    if 'agents_used' in result:
        summary.append(f"\nAgents Used: {', '.join(result['agents_used'])}")

    if 'package_status' in result:
        summary.append(f"\nStatus: {result['package_status']}")

    summary.append("=" * 70)

    return "\n".join(summary)
