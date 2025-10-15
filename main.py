"""
KYC Verification System - Flow-Based Entry Point

This version uses CrewAI Flow for advanced state management,
conditional branching, and event-driven execution.
"""

import logging
import os
import argparse
import sys
from datetime import datetime
from typing import List
from dotenv import load_dotenv

from flows.kyc_verification_flow import KYCVerificationFlow
from tools.metadata_extractor_tool import MetadataExtractorTool, categorize_files_by_type
from tools.pdf_processor_tool import PDFProcessorTool
from utils.output_handler import process_and_save_results, create_output_summary

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def prepare_documents(file_paths: List[str]) -> tuple:
    """
    Prepare documents for Flow processing.

    Args:
        file_paths: List of file paths to process

    Returns:
        Tuple of (documents, metadata, categorized_files)
    """
    logger.info("=" * 70)
    logger.info("KYC VERIFICATION SYSTEM - FLOW-BASED PROCESSING")
    logger.info("=" * 70)

    # Step 1: Categorize files
    logger.info(f"\nProcessing {len(file_paths)} file(s)...")
    categorized_files = categorize_files_by_type(file_paths)

    logger.info(f"File categories:")
    logger.info(f"  - Documents: {len(categorized_files['documents'])}")
    logger.info(f"  - Images: {len(categorized_files['images'])}")
    logger.info(f"  - Other: {len(categorized_files['other'])}")

    # Step 2: Extract metadata
    logger.info("\nExtracting file metadata...")
    metadata_tool = MetadataExtractorTool()
    pdf_tool = PDFProcessorTool()

    collected_metadata = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            continue

        # Extract basic metadata
        metadata = metadata_tool._run(file_path)

        # Extract PDF content if it's a PDF
        if file_path.lower().endswith('.pdf'):
            pdf_analysis = pdf_tool._run(file_path)
            metadata.update(pdf_analysis)

        collected_metadata.append(metadata)

    logger.info(f"Metadata extracted from {len(collected_metadata)} file(s)")

    # Step 3: Prepare document content
    logger.info("\nPreparing documents for Flow analysis...")
    document_contents = []

    for metadata in collected_metadata:
        content = {
            'file_name': metadata.get('file_name', 'unknown'),
            'file_path': metadata.get('file_path', ''),
            'file_type': metadata.get('file_type', 'unknown'),
            'text_content': ''
        }

        # Get text content from PDF analysis or read from file
        if 'pdf_analysis' in metadata:
            content['text_content'] = metadata['pdf_analysis'].get('text_content', '')
        elif metadata.get('file_type') == 'Text File':
            try:
                with open(metadata['file_path'], 'r', encoding='utf-8') as f:
                    file_content = f.read()
                content['text_content'] = file_content[:5000] + "..." if len(file_content) > 5000 else file_content
            except Exception as e:
                logger.warning(f"Could not read {metadata['file_path']}: {e}")
                content['text_content'] = f"[Error reading file: {str(e)}]"

        if content['text_content']:
            document_contents.append(content)

    logger.info(f"Prepared {len(document_contents)} document(s) for analysis\n")

    return document_contents, collected_metadata, categorized_files


def main():
    """
    Main execution function using CrewAI Flow.
    """
    parser = argparse.ArgumentParser(
        description="KYC Verification System - Flow-Based Processing"
    )
    parser.add_argument(
        "files",
        nargs="*",  # Changed from "+" to "*" to allow zero arguments
        help="Paths to files to process (default: documents/sample_kyc_document.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file path",
        default=os.path.join("outputs", "kyc_flow_results.json")
    )

    args = parser.parse_args()

    # Use default file if no files provided
    if not args.files:
        default_file = os.path.join("documents", "sample_kyc_document.txt")
        if os.path.exists(default_file):
            logger.info(f"No files specified, using default: {default_file}")
            args.files = [default_file]
        else:
            logger.error(f"ERROR: No files specified and default file not found: {default_file}")
            sys.exit(1)

    # Validate file paths
    invalid_files = [f for f in args.files if not os.path.exists(f)]
    if invalid_files:
        logger.error(f"ERROR: The following files do not exist: {invalid_files}")
        sys.exit(1)

    try:
        # Prepare documents
        documents, metadata, categorized_files = prepare_documents(args.files)

        if not documents:
            logger.error("No documents to process after preparation")
            sys.exit(1)

        # Initialize and run Flow
        logger.info("=" * 70)
        logger.info("STARTING CREWAI FLOW EXECUTION")
        logger.info("=" * 70)
        logger.info("\nFlow Architecture:")
        logger.info("  1. Document Processing -> Analyzes uploaded documents")
        logger.info("  2. KYC Data Extraction -> Extracts structured KYC data")
        logger.info("  3. Risk Assessment -> Evaluates customer risk profile")
        logger.info("  4. Risk-Based Routing -> Routes based on risk level")
        logger.info("  5. Finalization -> Compiles complete results\n")

        flow = KYCVerificationFlow(verbose=True)

        # Set documents in flow state before kickoff
        flow.documents = documents

        # Execute the flow
        flow_result = flow.kickoff()

        # Compile final package
        logger.info("\nCompiling final results package...")

        final_package = {
            "package_id": f"KYC_FLOW_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "processing_method": "crewai_flow",
            "total_files": len(args.files),
            "file_categories": {
                "images": len(categorized_files['images']),
                "documents": len(categorized_files['documents']),
                "other": len(categorized_files['other'])
            },
            "categorized_files": categorized_files,
            "file_metadata": metadata,
            "flow_results": flow_result,
            "agents_used": ["KYC Document Analysis Specialist"],
            "package_status": "COMPLETED"
        }

        # Display summary
        print("\n" + "=" * 70)
        print("KYC VERIFICATION FLOW - EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Package ID: {final_package['package_id']}")
        print(f"Files Processed: {final_package['total_files']}")
        print(f"Risk Level: {flow_result.get('kyc_verification', {}).get('risk_level', 'UNKNOWN')}")
        print(f"Compliance Status: {flow_result.get('kyc_verification', {}).get('compliance_status', 'UNKNOWN')}")
        print(f"Execution Time: {flow_result.get('execution_time', 0):.2f}s")
        print("=" * 70)

        # Save results
        if process_and_save_results(final_package):
            logger.info(f"\nResults saved to {args.output}")
            logger.info("=" * 70)
            logger.info("KYC VERIFICATION FLOW COMPLETE")
            logger.info("=" * 70)
        else:
            logger.warning("Failed to save results (non-critical)")

        return final_package

    except Exception as e:
        logger.error(f"\nERROR: Flow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
