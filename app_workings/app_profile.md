# PipesHub AI - Comprehensive Technical Architecture

## Overview

**PipesHub AI** is an enterprise workplace AI platform that enables organizations to search, analyze, and interact with their distributed data across multiple applications (Google Workspace, Microsoft 365, Slack, Jira, etc.) using natural language queries. The platform combines semantic search, AI-powered Q&A, and knowledge graph technology to provide intelligent insights with proper citations and source tracking.

## System Architecture

### High-Level Architecture

The application follows a microservices architecture with the following core components:

1. **Frontend**: React/TypeScript SPA with Material-UI
2. **Node.js Backend**: Authentication, user management, and API gateway
3. **Python Services**: Three specialized microservices for AI operations
4. **Infrastructure**: Multi-database setup with message queuing
5. **AI/ML Pipeline**: Document processing, embedding, and retrieval

---

## Frontend Architecture

### Technology Stack

- **Framework**: React 18.3.1 with TypeScript
- **Build Tool**: Vite (replacing traditional bundlers)
- **UI Library**: Material-UI v5.16.7 (@mui/material)
- **State Management**: Redux Toolkit (@reduxjs/toolkit)
- **Routing**: React Router
- **HTTP Client**: Axios
- **Authentication**: JWT with refresh tokens
- **Rich Text**: TipTap editor for document editing
- **Charts**: ApexCharts for data visualization
- **Styling**: Emotion for CSS-in-JS

### Key Frontend Components

#### 1. Authentication System (`src/auth/`)
- **JWT-based authentication** with refresh token support
- **Multi-factor authentication** (MFA) support
- **OAuth providers**: Google, Microsoft, Azure AD, SAML SSO
- **Session management** with Redis backend
- **Route protection** with auth guards

**Key Files:**
- `src/auth/context/jwt/auth-provider.tsx`: Main authentication context
- `src/auth/view/auth/authentication-view.tsx`: Login flow orchestration
- `src/auth/guard/auth-guard.tsx`: Route protection

#### 2. Chat Interface (`src/sections/qna/chatbot/`)
- **Real-time streaming** chat interface
- **Citation system** with source document linking
- **Conversation management** with history
- **File upload** and document attachment
- **Follow-up questions** generation

**Key Files:**
- `src/sections/qna/chatbot/chat-bot.tsx`: Main chat interface
- `src/sections/qna/chatbot/components/citations-hover-card.tsx`: Citation display

#### 3. Knowledge Base Management (`src/sections/knowledgebase/`)
- **Document browsing** and search
- **Connector status** monitoring
- **File management** with upload/download
- **Indexing status** tracking

#### 4. Layout System (`src/layouts/`)
- **Dashboard layout** with sidebar navigation
- **Authentication layouts** for login flows
- **Responsive design** with mobile support

### API Integration

The frontend communicates with multiple backend services:

```typescript
// Main API endpoints
const endpoints = {
  auth: '/api/v1/userAccount',
  search: '/api/v1/search',
  conversations: '/api/v1/conversations',
  knowledgeBase: '/api/v1/knowledgeBase',
  connectors: '/api/v1/connectors'
};
```

### State Management

Uses Redux Toolkit for:
- **Authentication state** (user, tokens, permissions)
- **User and groups** management
- **Application settings** and preferences

---

## Backend Architecture

### Node.js Backend (`backend/nodejs/`)

#### Technology Stack
- **Framework**: Express.js with TypeScript
- **Dependency Injection**: Inversify for IoC container
- **Authentication**: JWT, OAuth 2.0, SAML
- **Database**: MongoDB with Mongoose
- **Caching**: Redis
- **Message Queue**: Kafka
- **Configuration**: ETCD for distributed configuration

#### Core Modules

##### 1. Authentication Module (`src/modules/auth/`)
**Purpose**: Handles user authentication and authorization

**Key Components:**
- **Multi-step authentication** flow with session management
- **OAuth 2.0 providers**: Google, Microsoft, Azure AD
- **SAML SSO** integration
- **JWT token** generation and validation
- **Session management** with Redis

**Key Files:**
- `controller/userAccount.controller.ts`: Authentication logic
- `middlewares/userAuthentication.middleware.ts`: Auth middleware
- `services/session.service.ts`: Session management

##### 2. User Management Module (`src/modules/user_management/`)
**Purpose**: User and organization management

**Features:**
- User CRUD operations
- Organization management
- User groups and permissions
- Role-based access control

##### 3. Enterprise Search Module (`src/modules/enterprise_search/`)
**Purpose**: Search orchestration and conversation management

**Features:**
- Semantic search coordination
- Conversation management
- Query routing to Python services
- Response aggregation

##### 4. Knowledge Base Module (`src/modules/knowledge_base/`)
**Purpose**: Document and connector management

**Features:**
- Document metadata management
- Connector status monitoring
- File upload/download handling
- Indexing coordination

##### 5. Configuration Manager Module (`src/modules/configuration_manager/`)
**Purpose**: Centralized configuration management

**Features:**
- ETCD integration
- Service configuration
- Environment-specific settings
- Runtime configuration updates

### Python Services (`backend/python/`)

#### Technology Stack
- **Framework**: FastAPI with async support
- **Dependency Injection**: dependency-injector
- **AI/ML**: LangChain, HuggingFace, OpenAI
- **Vector Database**: Qdrant
- **Graph Database**: ArangoDB
- **Document Processing**: Docling, PyMuPDF, OCR
- **Task Queue**: Celery
- **Caching**: Redis

#### Service Architecture

##### 1. Query Service (`app/query_main.py`)
**Port**: 8000
**Purpose**: Handles search queries and AI-powered Q&A

**Key Features:**
- **Semantic search** with vector similarity
- **Query decomposition** for complex questions
- **LLM integration** for answer generation
- **Citation tracking** and source attribution
- **Conversation context** management

**API Endpoints:**
- `/api/v1/search` - Semantic search
- `/api/v1/conversations` - Chat interface
- `/api/v1/records` - Document retrieval
- `/api/v1/agent` - AI agent interactions

**Key Files:**
- `modules/retrieval/retrieval_service.py`: Search logic
- `modules/qna/prompt_templates.py`: LLM prompts
- `utils/query_decompose.py`: Query analysis

##### 2. Connector Service (`app/connectors_main.py`)
**Port**: 8088
**Purpose**: Integrates with external data sources

**Supported Connectors:**
- **Google Workspace**: Drive, Gmail, Calendar
- **Microsoft 365**: OneDrive, SharePoint, Outlook (planned)
- **Communication**: Slack, Teams (planned)
- **Productivity**: Notion, Jira, Confluence (planned)

**Key Features:**
- **Real-time sync** with webhooks
- **Incremental updates** with change tracking
- **Permission mapping** from source systems
- **Rate limiting** and error handling

**Key Files:**
- `connectors/sources/google/`: Google integrations
- `connectors/services/`: Core connector logic
- `connectors/api/router.py`: API endpoints

##### 3. Indexing Service (`app/indexing_main.py`)
**Port**: 8091
**Purpose**: Processes and indexes documents

**Processing Pipeline:**
1. **Document parsing** (PDF, DOCX, XLSX, etc.)
2. **Text extraction** with OCR support
3. **Content chunking** for optimal retrieval
4. **Embedding generation** using AI models
5. **Metadata extraction** (departments, categories, topics)
6. **Vector storage** in Qdrant
7. **Graph relationships** in ArangoDB

**Key Files:**
- `modules/parsers/`: Document parsers
- `modules/extraction/`: Metadata extraction
- `modules/indexing/`: Indexing logic

---

## Database Architecture

### ArangoDB (Graph Database)
**Purpose**: Stores structured data and relationships

**Collections:**
- `records`: Document metadata
- `files`: File-specific information
- `users`: User accounts
- `organizations`: Organization data
- `permissions`: Access control
- `recordRelations`: Document relationships

**Key Features:**
- **Graph queries** for relationship traversal
- **Multi-model** support (document + graph)
- **ACID transactions**
- **Horizontal scaling**

### MongoDB (Document Database)
**Purpose**: User management and configuration

**Collections:**
- User accounts and profiles
- Organization settings
- Authentication configurations
- User groups and permissions

### Qdrant (Vector Database)
**Purpose**: Stores document embeddings for semantic search

**Features:**
- **High-performance** vector similarity search
- **Filtering** by metadata
- **Hybrid search** (dense + sparse vectors)
- **Clustering** for scalability

### Redis (Cache & Sessions)
**Purpose**: Caching and session management

**Usage:**
- Authentication sessions
- API response caching
- Rate limiting
- Temporary data storage

---

## Infrastructure & Deployment

### Docker Architecture

The application uses a multi-container Docker setup:

#### Main Application Container
```dockerfile
# Multi-stage build combining all services
FROM python:3.10
# Install Node.js, Python deps, build frontend
# Expose ports: 3000 (frontend), 8000 (query), 8088 (connectors), 8091 (indexing)
```

#### Supporting Services
- **ArangoDB**: Graph database (port 8529)
- **MongoDB**: Document database (port 27017)
- **Qdrant**: Vector database (ports 6333, 6334)
- **Redis**: Cache and sessions (port 6379)
- **Kafka + Zookeeper**: Message queue (ports 9092, 2181)
- **ETCD**: Configuration store (port 2379)

#### Deployment Configurations

1. **Development** (`docker-compose.dev.yml`)
   - Built from local source
   - Debug logging enabled
   - Volume mounts for development

2. **Production** (`docker-compose.prod.yml`)
   - Pre-built images from registry
   - Optimized for performance
   - Health checks and restart policies

3. **Ollama Integration** (`docker-compose.ollama-dev.yml`)
   - Includes local LLM support
   - Ollama service for offline AI models

### Environment Configuration

```bash
# Core settings
NODE_ENV=production
SECRET_KEY=your_encryption_key

# Database passwords
ARANGO_PASSWORD=your_arangodb_password
MONGO_PASSWORD=your_mongodb_password
QDRANT_API_KEY=your_qdrant_api_key

# Public URLs (for webhooks)
CONNECTOR_PUBLIC_BACKEND=https://your-domain.com
FRONTEND_PUBLIC_URL=https://your-frontend.com
```

---

## AI & Machine Learning Pipeline

### Embedding Models
- **Dense Embeddings**: BAAI/bge-large-en-v1.5 (768 dimensions)
- **Sparse Embeddings**: Qdrant/BM25 for keyword matching
- **Reranking**: BAAI/bge-reranker-base for result refinement

### LLM Integration
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude models
- **Local Models**: Ollama support for offline deployment
- **HuggingFace**: Open-source model integration

### Document Processing
- **PDF**: PyMuPDF, OCR with Tesseract
- **Office**: python-docx, openpyxl
- **Advanced**: Docling for complex layouts
- **Images**: OCR pipeline for scanned documents

### Query Processing
1. **Query Analysis**: Intent detection and decomposition
2. **Retrieval**: Hybrid search (semantic + keyword)
3. **Reranking**: Context-aware result scoring
4. **Generation**: LLM-based answer synthesis
5. **Citation**: Source attribution and linking

---

## Key File Responsibilities

### Frontend Core Files

#### `src/app.tsx`
- **Purpose**: Root application component
- **Responsibilities**: Provider setup, routing, global state
- **Connections**: All major contexts and providers

#### `src/utils/axios.tsx`
- **Purpose**: HTTP client configuration
- **Responsibilities**: Request/response interceptors, error handling
- **Connections**: All API calls throughout the app

#### `src/sections/qna/chatbot/chat-bot.tsx`
- **Purpose**: Main chat interface
- **Responsibilities**: Message handling, streaming, citations
- **Connections**: Backend chat APIs, document preview

### Backend Core Files

#### `backend/nodejs/apps/src/app.ts`
- **Purpose**: Express application setup
- **Responsibilities**: Middleware, routing, container initialization
- **Connections**: All service modules and middleware

#### `backend/python/app/query_main.py`
- **Purpose**: Query service entry point
- **Responsibilities**: FastAPI setup, dependency injection
- **Connections**: All query-related modules

#### `backend/python/app/connectors_main.py`
- **Purpose**: Connector service entry point
- **Responsibilities**: External API integrations, sync management
- **Connections**: Google APIs, webhook handling

#### `backend/python/app/indexing_main.py`
- **Purpose**: Indexing service entry point
- **Responsibilities**: Document processing pipeline
- **Connections**: Parsers, AI models, databases

### Database Schema Files

#### `backend/python/app/models/records.py`
- **Purpose**: Core data models
- **Responsibilities**: Record structure, validation
- **Connections**: ArangoDB collections, API responses

#### `backend/python/app/schema/arango/documents.py`
- **Purpose**: Database schema definitions
- **Responsibilities**: Data validation, constraints
- **Connections**: ArangoDB collections, data models

### Configuration Files

#### `backend/python/pyproject.toml`
- **Purpose**: Python dependencies and project metadata
- **Responsibilities**: Dependency management, build configuration
- **Connections**: All Python services

#### `frontend/package.json`
- **Purpose**: Frontend dependencies and scripts
- **Responsibilities**: Build process, development tools
- **Connections**: Frontend build pipeline

---

## Security Architecture

### Authentication Flow
1. **Email submission** → Organization lookup
2. **Multi-factor authentication** → Step-by-step verification
3. **JWT token generation** → Access and refresh tokens
4. **Session management** → Redis-based sessions

### Authorization
- **Role-based access control** (RBAC)
- **Organization-level isolation**
- **Document-level permissions** from source systems
- **API-level authorization** middleware

### Data Security
- **Encryption at rest** in databases
- **TLS/SSL** for all communications
- **API key management** for external services
- **Audit logging** for security events

---

## Performance & Scalability

### Caching Strategy
- **Redis caching** for frequently accessed data
- **API response caching** with TTL
- **Embedding caching** to avoid recomputation
- **Session caching** for authentication

### Database Optimization
- **Indexing strategy** for fast queries
- **Connection pooling** for database connections
- **Query optimization** with proper indexes
- **Sharding support** for large datasets

### AI Model Optimization
- **Model caching** to avoid reloading
- **Batch processing** for embeddings
- **Async processing** for long-running tasks
- **Resource management** for GPU usage

---

## Monitoring & Observability

### Logging
- **Structured logging** with JSON format
- **Service-specific loggers** for each component
- **Error tracking** with stack traces
- **Performance metrics** logging

### Health Checks
- **Service health endpoints** for monitoring
- **Database connectivity** checks
- **External API** availability checks
- **Resource utilization** monitoring

### Metrics
- **API response times** and throughput
- **Database query performance**
- **AI model inference times**
- **User activity metrics**

---

## Development Workflow

### Local Development
1. **Docker Compose** for local services
2. **Hot reloading** for development
3. **Environment variables** for configuration
4. **Database migrations** for schema changes

### Testing Strategy
- **Unit tests** for individual components
- **Integration tests** for API endpoints
- **End-to-end tests** for user flows
- **Performance tests** for scalability

### CI/CD Pipeline
- **Automated testing** on pull requests
- **Docker image building** and publishing
- **Deployment automation** with Docker Compose
- **Environment promotion** (dev → staging → prod)

---

## Future Roadmap

### Planned Features
- **Code search** capabilities
- **Workplace AI agents** for automation
- **MCP (Model Context Protocol)** integration
- **APIs and SDKs** for third-party integration
- **Personalized search** with user preferences
- **Kubernetes deployment** for high availability
- **PageRank algorithm** for result ranking

### Scalability Improvements
- **Microservices decomposition** for better scaling
- **Kubernetes orchestration** for container management
- **Database sharding** for large datasets
- **CDN integration** for global performance
- **Load balancing** for high availability

---

This comprehensive technical outline provides a complete understanding of the PipesHub AI platform architecture, from the frontend user interface to the backend AI services and infrastructure components. The system is designed for enterprise-scale deployment with security, performance, and scalability as core principles.
