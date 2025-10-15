from crewai import Agent
from tools.metadata_extractor_tool import MetadataExtractorTool
from tools.pdf_processor_tool import PDFProcessorTool
from utils.llm_config import get_llm_config


def create_document_processor_agent():
    """
    Create the Document Processor Agent with centralized LLM configuration.

    This agent specializes in analyzing KYC documents, extracting personal information,
    identification details, account information, and performing risk assessment.

    Returns:
        Configured Agent for document processing and KYC analysis
    """
    llm = get_llm_config()

    metadata_tool = MetadataExtractorTool()
    pdf_tool = PDFProcessorTool()

    agent = Agent(
        role="KYC Document Analysis Specialist",
        goal="Extract, analyze, and verify comprehensive KYC information from customer onboarding documents including personal data, identification details, account information, and risk assessment",
        backstory="""You are an expert KYC (Know Your Customer) analyst with deep knowledge of
        financial compliance, document verification, and customer onboarding processes. You specialize
        in analyzing identity documents, extracting personal information, validating identification
        details, and assessing customer risk profiles. You have extensive experience with AML
        (Anti-Money Laundering) regulations, PEP (Politically Exposed Person) screening, sanctions
        checking, and regulatory compliance. You can read PDF files, extract structured data from
        unstructured documents, identify key information points, and organize findings in a comprehensive
        KYC analysis report. Your analysis helps financial institutions make informed decisions about
        customer onboarding while ensuring regulatory compliance.""",
        llm=llm,
        tools=[metadata_tool, pdf_tool],
        verbose=True,
        allow_delegation=False
    )

    return agent
