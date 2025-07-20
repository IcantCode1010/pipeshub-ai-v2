# PipesHub AI - Metadata Extraction System Documentation

## Overview

The PipesHub AI system implements a sophisticated metadata extraction pipeline that processes documents of various formats and extracts structured metadata using Large Language Models (LLMs) and machine learning techniques. The system includes specialized extraction capabilities for aviation documents, providing enhanced metadata extraction for flight operations manuals and aircraft maintenance documentation. This document provides a comprehensive overview of all files, processes, and components involved in metadata extraction.

## Architecture Overview

```
Document Ingestion → Format-Specific Parsing → Domain Extraction → Database Storage → Vector Indexing
```

## Core Components

### 1. Primary Domain Extraction Module

**File**: `backend/python/app/modules/extraction/domain_extraction.py`

**Main Class**: `DomainExtractor`

**Key Responsibilities**:
- Document classification into departments, categories, and subcategories
- Language detection and sentiment analysis
- Topic extraction and similarity matching
- Summary generation
- Confidence scoring
- Database storage with relationship creation

**Key Methods**:
- `extract_metadata(content, org_id)` - Main extraction method using LLM
- `extract_aviation_metadata(content, org_id)` - Aviation-specific extraction with enhanced metadata
- `save_metadata_to_db(org_id, record_id, metadata, virtual_record_id)` - Saves extracted metadata to ArangoDB
- `save_summary_to_storage(org_id, record_id, virtual_record_id, summary)` - Stores document summaries

**Aviation Enhancement Features**:
- Specialized Pydantic models for aviation metadata validation
- Support for flight operations and maintenance-specific fields
- Aviation-focused topic similarity matching
- Safety-critical information prioritization

**Technologies Used**:
- Azure OpenAI for LLM-based extraction
- scikit-learn (TF-IDF, LDA) for topic similarity
- Pydantic for data validation

### 2. Extraction Configuration

**File**: `backend/python/app/modules/extraction/prompt_template.py`

Contains two comprehensive LLM prompt templates:

**Standard Prompt Template** (`prompt`):
- Classify documents into 1-3 departments from predefined lists
- Categorize into hierarchical categories (3 levels)
- Detect languages using ISO language names
- Analyze sentiment from predefined options
- Extract 3-6 relevant topics
- Generate confidence scores (0.0-1.0)
- Create concise summaries

**Aviation-Specific Prompt Template** (`aviation_prompt`):
- Enhanced extraction for flight manuals and maintenance documentation
- Aviation-specific department classification
- Safety-focused sentiment analysis (Safety Critical, Advisory, Routine, etc.)
- Precise aviation terminology for topics
- Additional metadata for flight operations:
  - Flight phases (preflight through shutdown)
  - Procedure types (Normal, Non-Normal, Emergency)
  - Affected aircraft systems
  - Checklist sections
- Additional metadata for maintenance:
  - Aircraft type codes (ICAO)
  - ATA chapter numbers
  - Maintenance types (Scheduled, MEL, AD, etc.)
  - Regulatory references
  - Components and tools

**Output Format**: Structured JSON with strict schema validation

### 3. Document Processing Pipeline

**File**: `backend/python/app/events/processor.py`

**Main Class**: `Processor`

**Supported Document Types**:
- PDF documents (with OCR support)
- Microsoft Office (DOCX, DOC, XLSX, XLS, PPTX, PPT)
- Google Workspace (Docs, Sheets, Slides)
- Web formats (HTML, Markdown, MDX)
- Text files (TXT, CSV)
- Email (Gmail messages)

**Key Processing Methods**:
- `process_pdf_document()` - PDF processing with automatic OCR
- `process_docx_document()` - Word document processing
- `process_excel_document()` - Excel spreadsheet processing
- `process_google_docs()` - Google Docs processing
- `process_html_document()` - HTML document processing
- And many more format-specific processors

**Common Processing Flow**:
1. Parse document using format-specific parser
2. Extract text content and structural information
3. Call `DomainExtractor.extract_metadata()` for domain-specific extraction
4. Create sentence data for vector indexing
5. Store results in database

### 4. Parser-Level Metadata Extraction

Each document format has specialized parsers that extract format-specific metadata:

#### PDF Parsers
- **`backend/python/app/modules/parsers/pdf/azure_document_intelligence_processor.py`**
- **`backend/python/app/modules/parsers/pdf/pymupdf_ocrmypdf_processor.py`**
- **`backend/python/app/modules/parsers/pdf/ocr_handler.py`**

**Extracted Metadata**:
- Page count and layout information
- OCR confidence scores
- Bounding box coordinates
- Block types (text, image, table, list, header)

#### Excel/Spreadsheet Parsers
- **`backend/python/app/modules/parsers/excel/excel_parser.py`**
- **`backend/python/app/modules/parsers/csv/csv_parser.py`**
- **`backend/python/app/modules/parsers/google_files/google_sheets_parser.py`**

**Extracted Metadata**:
- Sheet names and counts
- Row and column information
- Cell data and formulas
- Table structures

#### Document Parsers
- **`backend/python/app/modules/parsers/docx/docx_parser.py`**
- **`backend/python/app/modules/parsers/google_files/google_docs_parser.py`**

**Extracted Metadata**:
- Document structure (headings, paragraphs, tables)
- Formatting information
- Links and references
- Image and table counts

#### Presentation Parsers
- **`backend/python/app/modules/parsers/google_files/google_slides_parser.py`**

**Extracted Metadata**:
- Slide count and layout
- Element types (shapes, tables, images)
- Speaker notes
- Master slide information

### 5. Indexing Integration

**File**: `backend/python/app/modules/indexing/run.py`

**Main Class**: `IndexingPipeline`

**Key Responsibilities**:
- Process metadata for vector storage
- Enhance metadata with additional searchable fields
- Handle metadata merging for chunked documents
- Create vector embeddings with metadata

**Key Methods**:
- `_process_metadata(meta)` - Enhances metadata for indexing
- `_merge_metadata(metadata_list)` - Merges metadata from multiple chunks
- `index_documents(sentence_data)` - Creates vector embeddings with metadata

**Enhanced Metadata Fields**:
- `orgId`, `virtualRecordId`, `recordName`
- `blockType`, `blockNum`, `blockText`
- `departments`, `topics`, `categories`
- `languages`, `extension`, `mimeType`
- `pageNum`, `sheetName`, `sheetNum` (format-specific)

### 6. Database Schema & Storage

**File**: `backend/python/app/schema/arango/documents.py`

**Key Schema Fields**:
- `extractionStatus` - Tracks extraction progress
- `lastExtractionTimestamp` - Timestamp of last extraction
- `summaryDocumentId` - Reference to stored summary

**Database Collections**:
- `records` - Main document records
- `files` - File metadata
- `departments` - Department taxonomy
- `categories` - Category hierarchy
- `topics` - Topic entities
- `languages` - Language entities

### 7. Service Integration

#### Kafka Consumer
**File**: `backend/python/app/services/kafka_consumer.py`

**Responsibilities**:
- Receives document processing messages
- Updates extraction status during processing
- Handles error states and cleanup

#### Setup and Configuration
**File**: `backend/python/app/setups/indexing_setup.py`

**Responsibilities**:
- Dependency injection for DomainExtractor
- Service initialization and configuration
- Resource management

## Metadata Categories Extracted

### 1. Document Classification
- **Departments**: 1-3 departments from organization-specific taxonomy
- **Categories**: Hierarchical classification (3 levels)
  - Level 1: Broad category (e.g., "Legal", "Technical")
  - Level 2: Subcategory (e.g., "Contract", "Documentation")
  - Level 3: Specific type (e.g., "NDA", "API Guide")

### 2. Content Analysis
- **Topics**: 3-6 key themes extracted from content
- **Languages**: All detected languages using ISO names
- **Sentiment**: Overall document tone from predefined options
- **Summary**: Concise content summary

### 3. Quality Metrics
- **Confidence Score**: 0.0-1.0 indicating extraction certainty
- **Extraction Timestamp**: When metadata was last extracted
- **Processing Status**: Current state of extraction process

### 4. Technical Metadata
- **File Properties**: Extension, MIME type, size
- **Structure Info**: Page count, sheet count, element counts
- **Format-Specific**: Bounding boxes, cell references, slide numbers

### 5. Aviation-Specific Metadata (Enhanced Extraction)

#### Aviation Document Classification
- **Departments**: Aviation-specific departments including:
  - Flight Operations
  - Aircraft Maintenance
  - Air Traffic Control
  - Safety & Quality Assurance
  - Regulatory Compliance
  - Training & Certification
  - Ground Operations
  - Engineering & Technical Publications
  - Flight Dispatch
  - Emergency Response

- **Categories**: Either "Flight Operations" or "Aircraft Maintenance"
- **Aviation Sentiment Types**:
  - Safety Critical - Immediate safety implications
  - Advisory - Important operational guidance
  - Routine - Standard procedures
  - Positive - Performance improvements
  - Negative - Issues or failures
  - Regulatory - Compliance requirements

#### Flight Operations Metadata
- **Flight Phases**: preflight, pushback, taxi, takeoff, initial_climb, climb, cruise, descent, approach, landing, taxi_in, shutdown, turnaround
- **Procedure Type**: Normal, Non-Normal, or Emergency
- **Checklist Section**: Specific checklist names (e.g., "Before Start", "After Takeoff")
- **Systems Affected**: Aircraft systems (e.g., Hydraulic, Electrical, Pressurization)

#### Aircraft Maintenance Metadata
- **Aircraft Type**: ICAO type codes (e.g., B737, A320, B777)
- **ATA Chapter**: System/component chapter numbers
- **Maintenance Type**: Scheduled, Unscheduled, MEL, SB, AD, Modification
- **Regulatory References**: AD numbers, Service Bulletins, AMM references
- **Components Involved**: Specific parts and assemblies
- **Tools Required**: Special equipment needed

## Processing Flow

### 1. Document Ingestion
- Documents arrive via Kafka messages
- Initial validation and format detection
- Status updates to `IN_PROGRESS`

### 2. Format-Specific Parsing
- Route to appropriate parser based on file extension
- Extract text content and structural information
- Generate format-specific metadata

### 3. Domain Extraction
- Send text content to `DomainExtractor`
- LLM processes content using structured prompt
- Extract departments, categories, topics, sentiment
- Generate confidence scores and summaries

### 4. Database Storage
- Save extracted metadata to ArangoDB
- Create relationships between entities
- Update document status to `COMPLETED`

### 5. Vector Indexing
- Enhance metadata for search
- Create vector embeddings with metadata
- Store in Qdrant vector database

### 6. Error Handling
- Comprehensive error tracking
- Fallback mechanisms for parsing failures
- Status updates for failed extractions

## Configuration and Customization

### LLM Configuration
- Configurable Azure OpenAI endpoints
- Model selection (GPT-3.5, GPT-4)
- Token limits and chunking strategies

### Taxonomy Management
- Organization-specific department lists
- Configurable category hierarchies
- Custom sentiment options

### Processing Options
- OCR provider selection (Azure DI, PyMuPDF)
- Chunking strategies for large documents
- Merge vs. separate indexing options

## Error Handling and Monitoring

### Exception Types
- `ExtractionError` - General extraction failures
- `MetadataProcessingError` - Metadata processing issues
- `DocumentProcessingError` - Document-level errors

### Status Tracking
- Real-time status updates in database
- Comprehensive logging throughout pipeline
- Error details and recovery information

### Cleanup Mechanisms
- Stuck file detection and cleanup
- Automatic retry mechanisms
- Resource cleanup on failures

## Performance Considerations

### Optimization Strategies
- Document chunking for large files
- Batch processing for similar documents
- Caching of frequently accessed metadata

### Scalability Features
- Asynchronous processing pipeline
- Distributed processing via Kafka
- Vector database optimization

### Resource Management
- Memory-efficient parsing
- Temporary file cleanup
- Connection pooling for databases

## Future Enhancements

### Planned Improvements
- Enhanced topic modeling algorithms
- Multi-language extraction support
- Custom entity recognition
- Automated taxonomy expansion

### Integration Opportunities
- External knowledge bases
- Custom ML model integration
- Real-time extraction updates
- Advanced similarity matching

## Troubleshooting

### Common Issues
1. **Extraction Timeouts**: Large documents may require chunking
2. **Format Errors**: Unsupported file formats or corrupted files
3. **LLM Failures**: API limits or model unavailability
4. **Database Errors**: Connection issues or schema mismatches

### Debugging Tools
- Comprehensive logging throughout pipeline
- Status tracking in database
- Error details in exception handling
- Performance metrics collection

## Aviation-Specific Usage

### Enabling Aviation Extraction

To use the aviation-specific extraction for crew flight manuals and maintenance documents:

1. **Call the Aviation Method**: Use `extract_aviation_metadata()` instead of `extract_metadata()` when processing aviation documents
2. **Aviation Topics**: The system will automatically extract aviation-specific topics like:
   - Flight Operations: engine failure, emergency descent, go-around procedures, crew coordination
   - Maintenance: hydraulic leaks, AD compliance, MEL deferrals, component inspections
3. **Enhanced Safety Focus**: Aviation extraction prioritizes safety-critical information and regulatory compliance

### Example Aviation Metadata Output

```json
{
  "departments": ["Flight Operations", "Safety & Quality Assurance"],
  "category": "Flight Operations",
  "subcategories": {
    "level1": "Emergency Procedures",
    "level2": "Rapid Descent",
    "level3": "Cabin Altitude Uncontrollable"
  },
  "sentiment": "Safety Critical",
  "topics": ["emergency descent", "cabin pressurization", "oxygen masks"],
  "flight_operations_metadata": {
    "flight_phase": ["cruise", "descent"],
    "procedure_type": "Emergency",
    "checklist_section": "Emergency Descent",
    "systems_affected": ["Pressurization", "Oxygen"]
  }
}
```

### Aviation Document Best Practices

1. **Document Preparation**: Ensure aviation documents include clear references to:
   - Aircraft type and model
   - Regulatory references (AD numbers, SBs)
   - ATA chapter numbers for maintenance docs
   - Flight phase indicators

2. **Topic Consistency**: The system maintains consistency in aviation terminology through similarity matching

3. **Safety Prioritization**: Documents marked as "Safety Critical" receive priority processing and enhanced validation

## Confidence Score Utilization

### Overview

The system implements sophisticated confidence score utilization to improve extraction quality and efficiency without impacting performance. Confidence scores are used for automated routing, caching strategies, and quality monitoring.

### Confidence-Based Processing

#### Confidence Bands
- **HIGH (≥85%)**: Auto-approved, 24-hour cache, minimal review
- **MEDIUM (60-84%)**: Standard review queue, 12-hour cache
- **LOW (<60%)**: Enhanced review required, 1-hour cache

#### Aviation-Specific Thresholds
- **Safety Critical Documents**: Minimum 80% confidence required
- **Emergency Procedures**: Flagged for immediate review if <80%
- **Maintenance Documents**: AD/SB references verified at higher thresholds

### Automated Routing

#### Processing Paths
1. **Auto-Approve Path** (≥85% confidence)
   - Immediate indexing
   - Extended cache TTL
   - Spot-check quality monitoring

2. **Standard Review Path** (60-84% confidence)
   - Queue for human review
   - Standard cache TTL
   - Normal processing priority

3. **Enhanced Review Path** (30-59% confidence)
   - Detailed human review required
   - Short cache TTL
   - Higher processing priority

4. **Manual Validation Path** (<30% confidence)
   - Complete manual processing
   - No caching
   - Immediate attention required

#### Safety Critical Override
- Safety critical documents with <80% confidence bypass normal routing
- Immediate urgent review queue placement
- Special monitoring and alerting

### Quality Monitoring

#### Real-Time Metrics
- **Overall Confidence Trends**: Track extraction quality over time
- **Department-Specific Performance**: Monitor confidence by document type
- **Safety Critical Tracking**: Special monitoring for aviation safety docs
- **Review Queue Management**: Automatic prioritization and workload distribution

#### Alerting System
- **Declining Confidence Trends**: Automatic alerts when quality drops
- **Safety Critical Low Confidence**: Immediate notifications
- **High Review Volume**: Capacity planning alerts
- **System Health**: Performance and reliability monitoring

### Caching Strategy

#### Confidence-Based TTL
```python
# Cache duration based on confidence
HIGH_CONFIDENCE = 86400 seconds    # 24 hours
MEDIUM_CONFIDENCE = 43200 seconds  # 12 hours  
LOW_CONFIDENCE = 3600 seconds      # 1 hour
```

#### Cache Optimization
- High confidence documents cached longer
- Low confidence documents cached briefly
- Automatic cache invalidation for updated extractions
- Memory-efficient confidence metadata storage

### Performance Impact Mitigation

#### Asynchronous Processing
- Confidence routing happens in background
- No impact on extraction pipeline performance
- Deferred quality analysis and monitoring

#### Lightweight Operations
- Simple threshold checks (no heavy computation)
- Pre-computed confidence bands
- Bit-flag storage for ultra-fast lookups

#### Smart Defaults
- Graceful degradation when confidence processing is slow
- Fallback to standard processing if confidence system unavailable
- Optional confidence features (core functionality works without them)

### API Endpoints

#### Confidence Monitoring
- `GET /api/confidence/stats` - Overall confidence statistics
- `GET /api/confidence/review-queue` - Documents requiring review
- `GET /api/confidence/alerts` - System alerts and warnings
- `GET /api/confidence/metrics/summary` - Dashboard summary

#### Quality Management
- `POST /api/confidence/review-queue/{id}/resolve` - Mark review items as resolved
- `GET /api/confidence/health` - System health check

### Frontend Integration

#### Confidence Indicators
- Visual confidence scores in document lists
- Aviation-specific safety indicators
- Review status and priority indicators
- Trend visualization and alerts

#### Dashboard Features
- Real-time confidence monitoring
- Review queue management
- Quality trend analysis
- Alert management and resolution

## Conclusion

The PipesHub AI metadata extraction system provides a robust, scalable solution for processing diverse document formats and extracting meaningful metadata. The combination of specialized parsers, LLM-based analysis, and comprehensive database storage creates a powerful foundation for document understanding and search capabilities.

The aviation-specific enhancements make the system particularly well-suited for airline operations, providing precise categorization and metadata extraction for flight manuals and maintenance documentation. This ensures compliance with aviation safety standards while enabling efficient document retrieval and analysis.

The system's modular architecture allows for easy extension to new document formats and extraction techniques, while maintaining high performance and reliability through comprehensive error handling and monitoring.
