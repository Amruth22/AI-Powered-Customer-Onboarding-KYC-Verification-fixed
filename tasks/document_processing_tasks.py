from crewai import Task
from agents.document_processor_agent import create_document_processor_agent

agent = create_document_processor_agent()

document_processing_task = Task(
    description="""Analyze KYC documents and extract comprehensive customer information.

    You will receive a list of documents with their content. Your task is to:

    1. ANALYZE each document's text content thoroughly
    2. EXTRACT KYC-specific information including:
       - Personal Information: Full name, date of birth, address, phone, email, nationality
       - Identification Documents: ID numbers, passport numbers, license numbers, issue/expiry dates, issuing authorities
       - Account Information: Account types, initial deposits, source of funds, expected transaction volumes
       - Risk Assessment: Customer risk level (LOW/MEDIUM/HIGH), PEP status, sanctions screening results, AML flags
       - Compliance Verification: Declaration completeness, signature presence, document authenticity

    3. IDENTIFY key information, important data points, and document structure
    4. SUMMARIZE the main content and purpose of each document
    5. VALIDATE information completeness and flag any missing required fields
    6. ASSESS overall customer risk profile based on provided information
    7. ORGANIZE findings in a structured, comprehensive KYC analysis report

    For each document, pay special attention to:
    - Customer identification details and verification status
    - Financial information and source of funds documentation
    - Risk indicators and compliance red flags
    - Declaration and consent forms completeness
    - Document authenticity and potential fraud indicators

    Documents to analyze:
    {documents}

    Output: Comprehensive KYC analysis report with extracted personal information, identification
    details, account information, risk assessment, compliance verification status, and recommendations
    for customer onboarding approval or additional review requirements.""",
    agent=agent,
    expected_output="""Structured KYC analysis report in JSON format containing:
    - Personal Information section with all customer details
    - Identification Documents section with ID verification data
    - Account Information section with financial details
    - Risk Assessment section with risk level and flags
    - Compliance Verification section with completeness status
    - Overall Recommendation for onboarding (APPROVED/REVIEW_REQUIRED/REJECTED)
    - Missing Information list (if any)
    - Next Steps and additional requirements"""
)


kyc_extraction_task = Task(
    description="""Extract specific KYC data points from documents for regulatory compliance.

    Focus on extracting and structuring the following mandatory KYC information:

    PERSONAL INFORMATION:
    - Full legal name (as per government ID)
    - Date of birth (DD/MM/YYYY format)
    - Current residential address
    - Contact details (phone, email)
    - Nationality and citizenship status

    IDENTIFICATION:
    - Primary ID type and number
    - Issue date and expiration date
    - Issuing authority/country
    - Secondary ID (if available)

    ACCOUNT DETAILS:
    - Requested account type
    - Initial deposit amount
    - Source of funds
    - Purpose of account
    - Expected monthly transactions

    RISK FACTORS:
    - Customer risk classification
    - PEP status (Yes/No)
    - Sanctions screening result
    - Adverse media check
    - Country risk assessment

    COMPLIANCE:
    - Declaration signed (Yes/No)
    - Terms accepted (Yes/No)
    - Data consent provided (Yes/No)
    - All required documents present (Yes/No)

    Documents: {documents}

    Output: Structured data extraction with all KYC fields populated and validation status.""",
    agent=agent,
    expected_output="Complete KYC data extraction with all mandatory fields populated, validation flags, and data quality score"
)
