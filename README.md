# AI-Powered Customer Onboarding KYC Verification System

An intelligent document processing system for customer onboarding and KYC (Know Your Customer) verification using CrewAI Flow architecture with advanced state management and risk-based routing.

## Features

- **Advanced Flow Architecture**: 5-step CrewAI Flow pipeline with state management and conditional branching
- **Document Analysis**: AI-powered analysis of PDFs and text files using Gemini 2.0 Flash
- **Metadata Extraction**: Comprehensive file metadata extraction with BaseTool pattern
- **Text Content Extraction**: PDF text extraction using PyMuPDF with PyPDF2 fallback
- **KYC Information Extraction**: Automatic identification of personal information, ID documents, account details, and risk factors
- **Risk Assessment**: Intelligent risk scoring and classification (LOW/MEDIUM/HIGH)
- **Risk-Based Routing**: Automated routing to manual review, additional verification, or auto-approval
- **JSON Output**: Structured analysis results with comprehensive metadata
- **Command-Line Interface**: Easy-to-use CLI with default document support

## Prerequisites

- Python 3.9 or higher
- Google Gemini API key (get one from [Google AI Studio](https://aistudio.google.com/))
- Basic understanding of CrewAI framework

## Quick Start

### 1. Setup

```bash
# Clone the repository
git clone <repository-url>
cd AI-Powered-Customer-Onboarding-KYC-Verification-1

# Create virtual environment
python -m venv env
source env/Scripts/activate  # On Windows
# source env/bin/activate    # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/)

### 3. Run the System

```bash
# Activate virtual environment
source env/Scripts/activate

# Run with default document
python main.py

# Run with specific files
python main.py documents/sample_kyc_document.txt

# Process multiple files
python main.py documents/*.txt documents/*.pdf

# Custom output location
python main.py documents/sample_kyc_document.txt -o outputs/my_results.json
```

### 4. Run Tests

```bash
# Run the complete test suite (10 tests)
python tests.py
```

Expected output:
```
============================================================
TEST RESULTS SUMMARY
============================================================
Total Tests: 10
Passed: 10
Failed: 0
Skipped: 0
Success Rate: 100.0%
============================================================
```

## Project Structure

```
AI-Powered-Customer-Onboarding-KYC-Verification/
├── agents/                           # AI agent implementations
│   ├── __init__.py
│   └── document_processor_agent.py   # Factory function for agent creation
│
├── flows/                            # CrewAI Flow implementations
│   └── kyc_verification_flow.py      # 5-step Flow with state management
│
├── tasks/                            # Task definitions
│   └── document_processing_tasks.py  # Module-level task variables
│
├── tools/                            # BaseTool implementations
│   ├── metadata_extractor_tool.py    # Metadata extraction tool
│   └── pdf_processor_tool.py         # PDF processing tool
│
├── utils/                            # Utility modules
│   ├── llm_config.py                 # Centralized LLM configuration
│   └── output_handler.py             # Output processing and saving
│
├── configs/                          # Configuration files
│   └── app_config.json               # Application configuration
│
├── documents/                        # Sample documents
│   ├── sample_kyc_document.txt
│   └── sample_kyc_document.pdf
│
├── outputs/                          # Generated results
│   ├── kyc_analysis_complete.json
│   └── file_metadata.json
│
├── crew.py                           # Crew orchestration class
├── main.py                           # Flow-based entry point
├── tests.py                          # Comprehensive test suite (10 tests)
├── requirements.txt                  # Python dependencies
├── .env                              # API key configuration (create this)
├── .gitignore                        # Git ignore patterns
├── README.md                         # This file
├── ARCHITECTURE.md                   # System architecture documentation
└── FLOW_IMPLEMENTATION.md            # Flow implementation details
```

## System Architecture

### CrewAI Flow Pipeline (5 Steps)

```
┌─────────────────────────────────────────────────┐
│  Step 1: Document Processing                   │
│  - Analyzes uploaded documents                 │
│  - Extracts text content                       │
│  - Validates document quality                  │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 2: KYC Data Extraction                   │
│  - Extracts structured KYC information         │
│  - Identifies missing required fields          │
│  - Validates data completeness                 │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 3: Risk Assessment                       │
│  - Calculates risk score                       │
│  - Evaluates PEP status                        │
│  - Classifies: LOW/MEDIUM/HIGH                 │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 4: Risk-Based Routing                    │
│  - HIGH: Manual review required                │
│  - MEDIUM: Additional verification             │
│  - LOW: Auto-approval pathway                  │
└──────────────────┬──────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 5: Finalization                          │
│  - Compiles complete results                   │
│  - Generates compliance report                 │
│  - Saves structured output                     │
└─────────────────────────────────────────────────┘
```

### Key Components

**1. Agents (Factory Pattern)**
```python
from agents.document_processor_agent import create_document_processor_agent

agent = create_document_processor_agent()
```

**2. Tools (BaseTool Pattern)**
```python
from tools.metadata_extractor_tool import MetadataExtractorTool
from tools.pdf_processor_tool import PDFProcessorTool

metadata_tool = MetadataExtractorTool()
pdf_tool = PDFProcessorTool()
```

**3. Crew Orchestration**
```python
from crew import create_kyc_verification_crew

crew = create_kyc_verification_crew()
result = crew.run_kyc_verification(documents)
```

**4. Flow Execution**
```python
from flows.kyc_verification_flow import KYCVerificationFlow

flow = KYCVerificationFlow(verbose=True)
flow.documents = documents
result = flow.kickoff()
```

## KYC Information Extracted

### Personal Information
- Full name and aliases
- Date of birth
- Current and previous addresses
- Contact information (phone, email)
- Nationality and citizenship

### Identification Documents
- ID numbers (passport, driver's license, national ID)
- Issue and expiration dates
- Issuing authorities
- Document verification status

### Account Information
- Account types and purposes
- Initial deposit amounts
- Source of funds documentation
- Expected transaction volumes

### Risk Assessment
- Customer risk level (LOW/MEDIUM/HIGH)
- PEP (Politically Exposed Person) status
- Sanctions screening results
- AML (Anti-Money Laundering) flags

### Compliance Verification
- Declaration completeness
- Signature validation
- Document authenticity checks
- Missing information tracking

## Test Suite

The system includes 10 comprehensive tests:

1. **test_env_api_key_configuration** - Validates API key setup
2. **test_metadata_extraction_tool** - Tests metadata extraction
3. **test_pdf_processor_tool** - Tests PDF processing
4. **test_file_categorization** - Tests file type classification
5. **test_agent_creation** - Tests agent factory pattern
6. **test_flow_initialization** - Tests Flow state initialization
7. **test_document_processing_flow** - Tests complete Flow execution
8. **test_output_json_generation** - Tests JSON output structure
9. **test_risk_assessment_logic** - Tests risk scoring algorithm
10. **test_routing_decision** - Tests risk-based routing

Run tests with: `python tests.py`

## Configuration

### LLM Configuration (`configs/app_config.json`)

```json
{
  "llm_config": {
    "model": "gemini/gemini-2.0-flash",
    "max_tokens": 3000,
    "temperature": 0.0
  },
  "kyc_config": {
    "supported_document_types": [".pdf", ".txt", ".doc", ".docx"],
    "required_fields": [
      "full_name",
      "date_of_birth",
      "address",
      "id_number",
      "source_of_funds"
    ]
  }
}
```

### Environment Variables (`.env`)

```env
GEMINI_API_KEY=your_actual_api_key_here
```

## Output Format

Results are saved in JSON format with the following structure:

```json
{
  "package_id": "KYC_FLOW_20251015_123456",
  "created_at": "2025-10-15T12:34:56.789012",
  "processing_method": "crewai_flow",
  "total_files": 1,
  "file_categories": {
    "images": 0,
    "documents": 1,
    "other": 0
  },
  "flow_results": {
    "status": "completed",
    "execution_time": 11.25,
    "kyc_verification": {
      "risk_level": "LOW",
      "compliance_status": "APPROVED",
      "missing_fields": [],
      "recommendation": "auto_approval"
    }
  }
}
```

## Dependencies

**Required Python Packages** (in requirements.txt):
- crewai>=0.11.0
- python-dotenv>=1.0.0
- Pillow>=10.0.0
- PyPDF2>=3.0.1
- PyMuPDF>=1.23.0

**External Services**:
- Google Gemini API (Gemini 2.0 Flash model)

## Advanced Usage

### Custom Workflows with Crew Orchestration

```python
from crew import create_kyc_verification_crew

crew = create_kyc_verification_crew()

# Full KYC verification
result = crew.run_kyc_verification(documents)

# KYC extraction only
result = crew.run_kyc_extraction_only(documents)

# Document processing only
result = crew.run_document_processing_only(documents)

# Custom workflow
result = crew.run_custom_workflow(
    documents,
    agents=['document_processor'],
    tasks=['document_processing']
)
```

### Direct Flow Execution

```python
from flows.kyc_verification_flow import KYCVerificationFlow

flow = KYCVerificationFlow(verbose=True)
flow.documents = prepared_documents
result = flow.kickoff()

# Access flow state
print(f"Risk Level: {flow.risk_level}")
print(f"Compliance Status: {flow.compliance_status}")
print(f"Missing Fields: {flow.missing_fields}")
```

## Troubleshooting

### API Key Issues

If you see authentication errors:
1. Verify `.env` file exists in root directory
2. Check API key is valid at [Google AI Studio](https://aistudio.google.com/)
3. Ensure no extra spaces in `.env` file

### Import Errors

If you see module import errors:
```bash
# Ensure virtual environment is activated
source env/Scripts/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Test Failures

If tests fail:
1. Check API key is configured
2. Verify sample documents exist in `documents/` folder
3. Run tests with verbose output: `python tests.py -v`

## Documentation

- **ARCHITECTURE.md** - Detailed system architecture and design patterns
- **FLOW_IMPLEMENTATION.md** - CrewAI Flow implementation details
- **CrewAI Documentation** - https://docs.crewai.com/
- **Gemini AI Documentation** - https://ai.google.dev/

## License

This project is for educational and evaluation purposes.

---

**Built with CrewAI Flow • Powered by Gemini 2.0 Flash**
