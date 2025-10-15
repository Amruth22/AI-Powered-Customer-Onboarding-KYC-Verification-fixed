"""
KYC Verification Flow - CrewAI Flow Implementation

This module implements the CrewAI Flow for orchestrating the KYC Verification process
with state management, conditional branching, and event-driven execution.
"""

from crewai.flow.flow import Flow, listen, start
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from crewai import Crew, Process
from agents.document_processor_agent import create_document_processor_agent
from tasks.document_processing_tasks import document_processing_task, kyc_extraction_task

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KYCVerificationFlow(Flow):
    """
    Main Flow orchestrating the KYC Verification process.

    This Flow provides:
    - State management across different stages
    - Conditional branching based on document quality
    - Event-driven execution of crews
    - Dynamic routing based on risk assessment
    - Comprehensive error handling
    """

    # State variables that persist across the flow
    documents: List[Dict] = []
    document_count: int = 0
    file_metadata: List[Dict] = []
    kyc_data: Dict = {}
    risk_level: str = "UNKNOWN"
    compliance_status: str = "PENDING"
    missing_fields: List[str] = []
    execution_start: Optional[datetime] = None
    execution_metrics: Dict = {}

    def __init__(self, verbose: bool = True):
        """
        Initialize the KYC Verification Flow.

        Args:
            verbose: Whether to enable verbose logging
        """
        super().__init__()
        self.verbose = verbose
        self.execution_start = datetime.now()
        logger.info("Starting KYC Verification Flow")

    @start()
    def initiate_document_processing(self) -> Dict[str, Any]:
        """
        Step 1: Document Processing Phase

        Processes uploaded documents through:
        - Metadata extraction
        - Content analysis
        - Quality assessment

        Args:
            None (uses self.documents from Flow state)

        Returns:
            Dictionary containing processing results
        """
        logger.info("\n" + "="*70)
        logger.info("FLOW STEP 1: DOCUMENT PROCESSING")
        logger.info("="*70)
        logger.info(f"Processing {len(self.documents)} document(s)...")

        step_start = datetime.now()

        try:
            self.document_count = len(self.documents)

            # Create document processing crew
            doc_agent = create_document_processor_agent()

            crew = Crew(
                agents=[doc_agent],
                tasks=[document_processing_task],
                verbose=self.verbose,
                process=Process.sequential
            )

            # Execute document processing
            result = crew.kickoff(inputs={'documents': self.documents})

            # Parse and store results
            if hasattr(result, 'raw'):
                result_data = result.raw
            else:
                result_data = str(result)

            duration = (datetime.now() - step_start).total_seconds()
            self.execution_metrics['document_processing'] = duration

            logger.info(f"Document processing completed in {duration:.2f}s")

            return {
                "status": "completed",
                "documents_processed": self.document_count,
                "analysis": result_data,
                "duration": duration
            }

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "documents_processed": 0
            }

    @listen("initiate_document_processing")
    def extract_kyc_data(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 2: KYC Data Extraction Phase

        Extracts structured KYC information:
        - Personal information
        - Identification details
        - Account information
        - Risk factors

        Args:
            processing_result: Results from document processing

        Returns:
            Dictionary containing extracted KYC data
        """
        logger.info("\n" + "="*70)
        logger.info("FLOW STEP 2: KYC DATA EXTRACTION")
        logger.info("="*70)

        # Conditional: Skip if processing failed
        if processing_result.get('status') == 'failed':
            logger.warning("Skipping KYC extraction due to processing failure")
            return {
                "status": "skipped",
                "reason": "processing_failed"
            }

        logger.info("Extracting structured KYC data...")
        step_start = datetime.now()

        try:
            # Create KYC extraction crew
            kyc_agent = create_document_processor_agent()

            crew = Crew(
                agents=[kyc_agent],
                tasks=[kyc_extraction_task],
                verbose=self.verbose,
                process=Process.sequential
            )

            # Execute KYC extraction
            result = crew.kickoff(inputs={'documents': self.documents})

            # Parse results
            if hasattr(result, 'raw'):
                result_data = result.raw
            else:
                result_data = str(result)

            # Update state
            self.kyc_data = self._parse_kyc_data(result_data)
            self.missing_fields = self._identify_missing_fields(self.kyc_data)

            duration = (datetime.now() - step_start).total_seconds()
            self.execution_metrics['kyc_extraction'] = duration

            logger.info(f"KYC extraction completed in {duration:.2f}s")
            logger.info(f"Missing fields: {len(self.missing_fields)}")

            return {
                "status": "completed",
                "kyc_data": self.kyc_data,
                "missing_fields": self.missing_fields,
                "duration": duration
            }

        except Exception as e:
            logger.error(f"KYC extraction failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    @listen("extract_kyc_data")
    def assess_risk_level(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Risk Assessment Phase

        Assesses customer risk based on:
        - PEP status
        - Source of funds
        - Country risk
        - Transaction patterns

        Args:
            extraction_result: Results from KYC extraction

        Returns:
            Dictionary containing risk assessment
        """
        logger.info("\n" + "="*70)
        logger.info("FLOW STEP 3: RISK ASSESSMENT")
        logger.info("="*70)

        if extraction_result.get('status') != 'completed':
            logger.warning("Skipping risk assessment due to extraction issues")
            self.risk_level = "UNKNOWN"
            return {
                "status": "skipped",
                "risk_level": "UNKNOWN"
            }

        logger.info("Assessing customer risk profile...")

        try:
            # Simple risk assessment logic
            risk_score = 0

            # Check for missing fields
            if len(self.missing_fields) > 3:
                risk_score += 2

            # Check PEP status (would parse from kyc_data)
            kyc_str = str(self.kyc_data).lower()
            if 'pep' in kyc_str and 'yes' in kyc_str:
                risk_score += 3

            # Determine risk level
            if risk_score >= 5:
                self.risk_level = "HIGH"
            elif risk_score >= 3:
                self.risk_level = "MEDIUM"
            else:
                self.risk_level = "LOW"

            logger.info(f"Risk assessment completed: {self.risk_level}")

            return {
                "status": "completed",
                "risk_level": self.risk_level,
                "risk_score": risk_score,
                "factors": {
                    "missing_fields": len(self.missing_fields),
                    "pep_status": "pep" in kyc_str
                }
            }

        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            self.risk_level = "UNKNOWN"
            return {
                "status": "failed",
                "error": str(e),
                "risk_level": "UNKNOWN"
            }

    @listen("assess_risk_level")
    def route_by_risk_level(self, risk_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 4: Risk-Based Routing

        Routes execution based on risk level:
        - HIGH risk: Requires manual review
        - MEDIUM risk: Additional verification
        - LOW risk: Auto-approval consideration

        Args:
            risk_result: Results from risk assessment

        Returns:
            Dictionary containing routing decision
        """
        logger.info("\n" + "="*70)
        logger.info("FLOW STEP 4: ROUTING DECISION")
        logger.info("="*70)

        if self.risk_level == "HIGH":
            logger.warning(f"HIGH RISK customer - routing to manual review")
            self.compliance_status = "MANUAL_REVIEW_REQUIRED"
            return {
                "route": "manual_review",
                "reason": "high_risk",
                "status": self.compliance_status
            }
        elif self.risk_level == "MEDIUM":
            logger.info("MEDIUM RISK customer - additional verification required")
            self.compliance_status = "ADDITIONAL_VERIFICATION"
            return {
                "route": "additional_verification",
                "reason": "medium_risk",
                "status": self.compliance_status
            }
        else:
            logger.info("LOW RISK customer - proceeding to approval")
            self.compliance_status = "APPROVED"
            return {
                "route": "auto_approval",
                "reason": "low_risk",
                "status": self.compliance_status
            }

    @listen("route_by_risk_level")
    def finalize_kyc_verification(self, routing_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 5: Finalization Phase

        Finalizes the KYC verification and returns complete results.

        Args:
            routing_result: Results from routing decision

        Returns:
            Dictionary containing complete verification results
        """
        logger.info("\n" + "="*70)
        logger.info("FLOW STEP 5: FINALIZATION")
        logger.info("="*70)

        total_duration = (datetime.now() - self.execution_start).total_seconds()

        final_result = {
            "status": "completed",
            "execution_time": total_duration,
            "metrics": self.execution_metrics,
            "kyc_verification": {
                "documents_processed": self.document_count,
                "kyc_data": self.kyc_data,
                "risk_level": self.risk_level,
                "compliance_status": self.compliance_status,
                "missing_fields": self.missing_fields,
                "recommendation": routing_result.get('route', 'unknown')
            }
        }

        logger.info("\n" + "="*70)
        logger.info("KYC VERIFICATION FLOW COMPLETED")
        logger.info("="*70)
        logger.info(f"Total execution time: {total_duration:.2f}s")
        logger.info(f"Documents processed: {self.document_count}")
        logger.info(f"Risk Level: {self.risk_level}")
        logger.info(f"Compliance Status: {self.compliance_status}")
        logger.info(f"Missing Fields: {len(self.missing_fields)}")
        logger.info("="*70)

        return final_result

    # Helper methods

    def _parse_kyc_data(self, result_data: str) -> Dict:
        """Parse KYC data from crew result."""
        # In production, this would parse structured JSON output
        return {
            "parsed": True,
            "source": "crew_result",
            "data_points": 15
        }

    def _identify_missing_fields(self, kyc_data: Dict) -> List[str]:
        """Identify missing required KYC fields."""
        required_fields = [
            "full_name", "date_of_birth", "address",
            "id_number", "source_of_funds"
        ]

        missing = []
        # Simple check - in production would check actual data structure
        kyc_str = str(kyc_data).lower()
        for field in required_fields:
            if field not in kyc_str:
                missing.append(field)

        return missing
