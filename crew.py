from crewai import Crew, Process
from typing import Any, Optional, List
import logging
from datetime import datetime

from agents.document_processor_agent import create_document_processor_agent

from tasks.document_processing_tasks import document_processing_task, kyc_extraction_task

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KYCVerificationCrew:
    """
    Main crew orchestration class for the KYC Verification System.

    This class encapsulates all crew-related logic and provides a clean
    interface for running different workflows.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize the crew orchestrator.

        Args:
            verbose: Whether to enable verbose output during execution
        """
        self.verbose = verbose
        self.agents = {}
        self.tasks = {}
        self._initialize_agents()
        self._initialize_tasks()
        logger.info("KYC Verification Crew initialized successfully")

    def _initialize_agents(self):
        """Initialize all agents for the crew."""
        logger.info("Initializing agents...")

        self.agents = {
            'document_processor': create_document_processor_agent()
        }

        logger.info(f"Initialized {len(self.agents)} agent(s)")

    def _initialize_tasks(self):
        """Initialize all tasks for the crew."""
        logger.info("Initializing tasks...")

        self.tasks = {
            'document_processing': document_processing_task,
            'kyc_extraction': kyc_extraction_task
        }

        logger.info(f"Initialized {len(self.tasks)} task(s)")

    def create_crew(
        self,
        agents: Optional[List[str]] = None,
        tasks: Optional[List[str]] = None,
        process: Process = Process.sequential
    ) -> Crew:
        """
        Create a crew with specified agents and tasks.

        Args:
            agents: List of agent keys to include (default: all agents)
            tasks: List of task keys to include (default: all tasks)
            process: CrewAI process type (sequential or hierarchical)

        Returns:
            Configured Crew instance
        """
        agent_keys = agents or list(self.agents.keys())
        task_keys = tasks or list(self.tasks.keys())

        selected_agents = [self.agents[key] for key in agent_keys if key in self.agents]
        selected_tasks = [self.tasks[key] for key in task_keys if key in self.tasks]

        logger.info(f"Creating crew with {len(selected_agents)} agent(s) and {len(selected_tasks)} task(s)")

        crew = Crew(
            agents=selected_agents,
            tasks=selected_tasks,
            verbose=self.verbose,
            process=process
        )

        return crew

    def run_kyc_verification(self, documents: List[Any]) -> Any:
        """
        Run the complete KYC verification pipeline.

        This is the main workflow that processes documents and extracts KYC data.

        Args:
            documents: List of documents to process

        Returns:
            The result of the crew execution
        """
        logger.info("Starting KYC verification pipeline...")
        start_time = datetime.now()

        crew = self.create_crew(
            agents=['document_processor'],
            tasks=['document_processing']
        )

        result = crew.kickoff(inputs={'documents': documents})

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"KYC verification completed in {duration:.2f} seconds")

        return result

    def run_kyc_extraction_only(self, documents: List[Any]) -> Any:
        """
        Run KYC data extraction workflow only.

        This workflow focuses on extracting structured KYC information.

        Args:
            documents: List of documents to process

        Returns:
            The result of the crew execution
        """
        logger.info("Starting KYC extraction workflow...")
        start_time = datetime.now()

        crew = self.create_crew(
            agents=['document_processor'],
            tasks=['kyc_extraction']
        )

        result = crew.kickoff(inputs={'documents': documents})

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"KYC extraction completed in {duration:.2f} seconds")

        return result

    def run_document_processing_only(self, documents: List[Any]) -> Any:
        """
        Run document processing workflow only.

        This workflow focuses on document analysis and validation.

        Args:
            documents: List of documents to process

        Returns:
            The result of the crew execution
        """
        logger.info("Starting document processing workflow...")
        start_time = datetime.now()

        crew = self.create_crew(
            agents=['document_processor'],
            tasks=['document_processing']
        )

        result = crew.kickoff(inputs={'documents': documents})

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Document processing completed in {duration:.2f} seconds")

        return result

    def run_custom_workflow(
        self,
        documents: List[Any],
        agents: List[str],
        tasks: List[str],
        process: Process = Process.sequential
    ) -> Any:
        """
        Run a custom workflow with specified agents and tasks.

        Args:
            documents: List of documents to process
            agents: List of agent keys to include
            tasks: List of task keys to include
            process: CrewAI process type

        Returns:
            The result of the crew execution
        """
        logger.info(f"Starting custom workflow with agents: {agents}, tasks: {tasks}")
        start_time = datetime.now()

        crew = self.create_crew(agents=agents, tasks=tasks, process=process)
        result = crew.kickoff(inputs={'documents': documents})

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Custom workflow completed in {duration:.2f} seconds")

        return result

    def get_agent(self, agent_key: str):
        """Get a specific agent by key."""
        return self.agents.get(agent_key)

    def get_task(self, task_key: str):
        """Get a specific task by key."""
        return self.tasks.get(task_key)

    def list_available_agents(self) -> List[str]:
        """Get list of available agent keys."""
        return list(self.agents.keys())

    def list_available_tasks(self) -> List[str]:
        """Get list of available task keys."""
        return list(self.tasks.keys())


def create_kyc_verification_crew(verbose: bool = True) -> KYCVerificationCrew:
    """
    Create and return a KYC Verification Crew instance.

    Args:
        verbose: Whether to enable verbose output

    Returns:
        KYCVerificationCrew instance
    """
    return KYCVerificationCrew(verbose=verbose)


def run_kyc_verification(documents: List[Any], verbose: bool = True) -> Any:
    """
    Quick function to run the KYC verification pipeline.

    Args:
        documents: List of documents to process
        verbose: Whether to enable verbose output

    Returns:
        The result of the crew execution
    """
    crew_orchestrator = KYCVerificationCrew(verbose=verbose)
    return crew_orchestrator.run_kyc_verification(documents)
