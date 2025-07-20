# PipesHub AI - Project Brief

## Project Overview

**PipesHub AI** is an enterprise workplace AI platform that enables organizations to search, analyze, and interact with their distributed data across multiple applications using natural language queries. The platform combines semantic search, AI-powered Q&A, and knowledge graph technology to provide intelligent insights with proper citations and source tracking.

## Core Requirements

### Primary Goals
1. **Unified Search**: Enable natural language search across multiple workplace applications (Google Workspace, Microsoft 365, Slack, Jira, etc.)
2. **AI-Powered Q&A**: Provide intelligent answers with proper citations and source attribution
3. **Knowledge Graph**: Structure all data into a powerful knowledge graph for relationship discovery
4. **Enterprise Security**: Maintain source-level permissions and data security
5. **Flexible Deployment**: Support both on-premise and cloud deployments

### Key Features
- **Multi-connector Support**: Google Drive, Gmail, Calendar, OneDrive, SharePoint, Slack, Notion, Jira, Confluence
- **Advanced Document Processing**: PDF (including scanned), DOCX, XLSX, PPTX, CSV, Markdown, HTML, Text
- **Real-time Indexing**: Both real-time and scheduled indexing capabilities
- **Citation System**: Proper source attribution with document linking
- **Multi-model AI**: Support for OpenAI, Anthropic, Google Gemini, AWS Bedrock, Cohere, local models via Ollama
- **Role-based Access**: Organization-level isolation with document-level permissions
- **Health Monitoring**: Real-time service health tracking with fallback capabilities

## Technical Architecture

### Core Components
1. **Frontend**: 
   - Main app: React/TypeScript SPA with Material-UI (port 3000)
   - Standalone frontend: Independent Vite-based React app (port 3001)
2. **Node.js Backend**: Authentication, user management, API gateway with rate limiting
3. **Python Services**: Three specialized microservices
   - Query Service (8000): LangGraph-based multi-agent AI workflows
   - Connector Service (8088): External data source integration
   - Indexing Service (8091): Document processing and vectorization
4. **Infrastructure**: Multi-database setup
   - ArangoDB: Knowledge graph database
   - MongoDB: Document storage
   - Qdrant: Vector database with hybrid search
   - Redis: Caching and session management
   - Kafka: Event streaming
   - ETCD: Distributed configuration management
5. **AI/ML Pipeline**: 
   - LangGraph for complex reasoning workflows
   - Multiple embedding models (OpenAI, Cohere, HuggingFace)
   - Reranking with BAAI/bge-reranker-base

### Service Architecture
- **Microservices Design**: Clear separation between API gateway, AI processing, and data ingestion
- **Event-Driven Processing**: Kafka-based event streaming for asynchronous operations
- **Configuration Management**: ETCD with AES-256-GCM encryption for sensitive configs
- **Security**: JWT authentication, CORS protection, rate limiting (100 req/15min)

## Current Features

### Search & AI Capabilities
- **Semantic Search**: Vector-based search with permission filtering
- **Hybrid Search**: Combined dense + sparse (BM25) search
- **Multi-step Reasoning**: LangGraph workflows (decompose → transform → retrieve → rerank → answer)
- **Citation Management**: Automatic source tracking and attribution
- **PDF Highlighting**: Interactive highlighting in Q&A responses

### User Interface
- **Multi-language Support**: English, Arabic, Chinese, French, Vietnamese
- **Dark/Light Themes**: 6 color schemes with responsive typography
- **OAuth Integration**: Google, Microsoft, SAML SSO support
- **Real-time Updates**: WebSocket-based notifications
- **Service Health Dashboard**: Visual status indicators with detailed diagnostics

### Enterprise Features
- **Organization Management**: Multi-tenant architecture with org-level isolation
- **User & Group Management**: Role-based access control
- **AI Model Configuration**: Flexible model selection per organization
- **Connector Configuration**: Per-org connector settings
- **Audit Logging**: Comprehensive activity tracking

### Document Processing
- **OCR Support**: Scanned document processing
- **Multi-format Extraction**: Unified text extraction across formats
- **Metadata Preservation**: Author, dates, tags maintained
- **Incremental Updates**: Delta processing for changed documents

## Current Status

The platform is in active development with:
- Core search and Q&A functionality implemented with LangGraph
- Google Workspace and Microsoft 365 connectors operational
- Advanced document processing pipeline with vectorization
- JWT authentication with OAuth providers integrated
- Rate limiting and security hardening complete
- Docker-based deployment with health monitoring
- Standalone frontend for enhanced user experience

## Recent Improvements (2025)

### Security Enhancements
- Implemented proper CORS configuration (replaced wildcards)
- Added express-rate-limit middleware globally
- Fixed package vulnerabilities (msal-node)
- Secured configuration management with encryption

### Architecture Updates
- Integrated LangGraph for multi-agent AI workflows
- Added hybrid search capabilities in Qdrant
- Implemented distributed configuration via ETCD
- Enhanced health monitoring across all services

### Frontend Improvements
- Created standalone frontend with Vite
- Added comprehensive service health monitoring
- Implemented fallback UI for service outages
- Fixed TypeScript configuration issues

## Deployment Options

1. **Development**: `docker-compose.dev.yml` - Built from source with debug logging
2. **Production**: `docker-compose.prod.yml` - Pre-built images optimized for performance
3. **Ollama Integration**: `docker-compose.ollama-dev.yml` - Includes local LLM support
4. **Single Container**: All services in one container with supervisord

## Technology Stack Summary

### Backend
- **Node.js**: Express, TypeScript, InversifyJS, Joi validation
- **Python**: FastAPI, LangChain, LangGraph, Pydantic
- **Databases**: ArangoDB, MongoDB, Qdrant, Redis
- **Message Queue**: Apache Kafka
- **Configuration**: ETCD

### Frontend
- **React 18**: Hooks, Context API, Suspense
- **Material-UI v5**: Comprehensive component library
- **State Management**: Redux Toolkit
- **Forms**: React Hook Form + Zod
- **Build Tools**: Vite (standalone), Webpack (main)
- **Internationalization**: i18next

### AI/ML
- **LLMs**: OpenAI, Anthropic, Google, AWS Bedrock, Ollama
- **Embeddings**: Multiple providers with 1536-dim support
- **Workflows**: LangGraph multi-agent architecture
- **Vector Search**: Qdrant with hybrid capabilities

## Future Roadmap

### Near-term
- Code search capabilities with syntax highlighting
- Workplace AI agents for task automation
- MCP (Model Context Protocol) integration
- Enhanced analytics and usage dashboards

### Medium-term
- APIs and SDKs for third-party integration
- Personalized search with user preferences
- Advanced knowledge graph visualizations
- Real-time collaboration features

### Long-term
- Kubernetes deployment for high availability
- PageRank algorithm for result ranking
- Multi-region deployment support
- Advanced AI agent marketplace

## Key Differentiators

1. **Knowledge Graph Foundation**: Unlike simple vector search, maintains relationships
2. **Multi-Agent AI**: LangGraph enables complex reasoning beyond simple RAG
3. **Enterprise-Ready**: Proper security, permissions, and audit trails
4. **Flexible Deployment**: On-premise, cloud, or hybrid options
5. **Open Architecture**: Extensible connector and AI model framework

## Success Metrics

- Query response time < 2 seconds
- 99.9% uptime for core services
- Support for 1M+ documents per organization
- Concurrent user support: 1000+ per instance
- Citation accuracy: 100% source attribution

## Contact & Resources

- Documentation: `/docs` endpoints on each service
- Health Monitoring: Built-in service status dashboard
- Configuration: ETCD-based with encryption
- Deployment: Docker Compose with production configs