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
- **Multi-model AI**: Support for OpenAI, Anthropic, local models via Ollama
- **Role-based Access**: Organization-level isolation with document-level permissions

## Technical Architecture

### Core Components
1. **Frontend**: React/TypeScript SPA with Material-UI
2. **Node.js Backend**: Authentication, user management, API gateway
3. **Python Services**: Three specialized microservices (Query, Connector, Indexing)
4. **Infrastructure**: Multi-database setup (ArangoDB, MongoDB, Qdrant, Redis)
5. **AI/ML Pipeline**: Document processing, embedding, and retrieval

### Service Ports
- Frontend: 3000
- Query Service: 8000
- Connector Service: 8088
- Indexing Service: 8091

## Current Status

The platform is in active development with:
- Core search and Q&A functionality implemented
- Google Workspace connectors operational
- Document processing pipeline functional
- Authentication and user management complete
- Docker-based deployment ready

## Deployment Options

1. **Development**: `docker-compose.dev.yml` - Built from source with debug logging
2. **Production**: `docker-compose.prod.yml` - Pre-built images optimized for performance
3. **Ollama Integration**: `docker-compose.ollama-dev.yml` - Includes local LLM support

## Future Roadmap

- Code search capabilities
- Workplace AI agents for automation
- MCP (Model Context Protocol) integration
- APIs and SDKs for third-party integration
- Personalized search with user preferences
- Kubernetes deployment for high availability
- PageRank algorithm for result ranking
