# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Docker Compose (Primary Development Method)
```bash
# Navigate to deployment directory
cd deployment/docker-compose

# Development build with all services
docker compose -f docker-compose.dev.yml -p pipeshub-ai up --build -d

# Production deployment
docker compose -f docker-compose.prod.yml -p pipeshub-ai up -d

# Stop services
docker compose -f docker-compose.dev.yml -p pipeshub-ai down

# View logs for specific service
docker compose -f docker-compose.dev.yml -p pipeshub-ai logs -f pipeshub-ai

# Restart single service (useful for code changes)
docker compose -f docker-compose.dev.yml -p pipeshub-ai restart pipeshub-ai
```

### Individual Service Development

**Node.js Backend** (backend/nodejs/apps/):
```bash
npm install          # Install dependencies first
npm run dev          # Development with nodemon
npm run build        # TypeScript compilation
npm run start        # Production start
npm run lint         # ESLint
npm run format       # Prettier formatting
npm run test         # Mocha tests
```

**Python AI Services** (backend/python/):
```bash
# Install dependencies
pip install -e .

# Run individual services
python -m app.query_main      # Query service (port 8000)
python -m app.indexing_main   # Indexing service (port 8091)
python -m app.connectors_main # Connector service (port 8088)

# Linting and formatting
ruff check .
ruff format .
```

**Frontend** (frontend/):
```bash
npm install          # Install dependencies (note: uses npm, not yarn)
npm run dev          # Development server
npm run build        # Production build
npm run start        # Preview build
npm run lint         # ESLint
npm run lint:fix     # Fix linting issues
npm run fm:check     # Prettier check
npm run fm:fix       # Fix formatting
```

## High-Level Architecture

### Microservices Overview
PipesHub AI is a workplace AI platform built on a microservices architecture with clear separation between API gateway, AI processing, and data ingestion services.

### Core Services
- **Node.js API Gateway** (port 3000): Authentication, user management, file storage, configuration management
- **Python Query Service** (port 8000): Semantic search, AI-powered Q&A with LangGraph workflows, multi-step reasoning
- **Python Indexing Service** (port 8091): Document processing, text extraction, vectorization, knowledge graph construction
- **Python Connector Service** (port 8088): Data ingestion from external sources (Google Workspace, Microsoft 365)

### Data Layer
- **ArangoDB** (port 8529): Knowledge graph database for documents and relationships, user-record access mappings
- **Qdrant** (port 6333): Vector database with hybrid dense+sparse (BM25) search capabilities
- **MongoDB** (port 27017): Document storage for unstructured data and file attachments
- **Redis** (port 6379): Caching, sessions, and LRU configuration cache
- **Kafka** (port 9092): Event streaming for real-time processing (`record-events`, `entity-events`, `sync-events`)
- **ETCD** (port 2379): Distributed configuration management with AES-256-GCM encryption

### AI/ML Stack
- **LangGraph**: Multi-agent workflows for complex reasoning (decompose → transform → retrieve → rerank → answer)
- **LangChain**: LLM orchestration and tool integration
- **Supported LLMs**: OpenAI, Anthropic, Google Gemini, AWS Bedrock, Ollama, Cohere
- **Embedding Models**: OpenAI, Cohere, HuggingFace BAAI/bge-large-en-v1.5, Sentence Transformers
- **Reranking**: BAAI/bge-reranker-base for result refinement

## Critical Architecture Patterns

### Inter-Service Communication
- **Node.js ↔ Python**: HTTP APIs with JWT token propagation
- **Service Discovery**: Environment variables for internal service URLs (`QUERY_BACKEND`, `INDEXING_BACKEND`, `CONNECTOR_BACKEND`)
- **Frontend ↔ Backend**: Axios HTTP client with global error handling and snackbar notifications
- **Authentication Flow**: Frontend OAuth/SAML → Node.js JWT issuance → Python service validation

### Configuration Management
- **ETCD-Based**: Distributed configuration store with hierarchical paths (`/services/arangodb`, `/services/aiModels`)
- **Encryption at Rest**: AES-256-GCM encryption for sensitive config values using `SECRET_KEY`
- **Runtime Updates**: ETCD watch mechanism with LRU cache (1000 entries) for performance
- **Service-Specific**: Each Python service accesses config via dependency-injected ConfigurationService

### Event-Driven Processing
- **Kafka Topics**: Document ingestion triggers events processed asynchronously
- **Processing Pipeline**: Connectors → Kafka events → Indexing service → Vector/Graph storage
- **Hybrid Search**: Permission-filtered vector search with accessible record ID constraints

### Security Implementation
- **Rate Limiting**: 100 requests/15min per IP (1000 in development) using express-rate-limit
- **JWT Authentication**: Shared secret validation across services with selective middleware
- **CORS Configuration**: Environment-specific origins with credential support
- **Input Validation**: Joi/Zod schemas in Node.js, Pydantic in Python services

## Development Workflow Patterns

### Dependency Injection
- **Node.js**: InversifyJS containers per feature module in `src/libs/types/container.types.ts`
- **Python**: dependency-injector framework with async container initialization
- **Service Wiring**: Containers self-wire on startup with modular service paths

### Error Handling Strategy
- **Centralized Middleware**: BaseError classes with structured HTTP responses
- **Request Context**: Request IDs and user context propagated through service calls
- **Environment-Aware**: Stack traces and metadata exposed only in development

### Database Connection Patterns
- **Connection Pooling**: Each service manages its own database connections independently
- **Health Checks**: Services verify database connectivity on startup with Docker health checks
- **Graceful Shutdown**: Proper resource cleanup on container stop signals

## Environment Configuration

### Required Environment Variables
Copy `deployment/docker-compose/env.template` to `.env` and configure:
- **SECRET_KEY**: AES encryption key for ETCD configuration values
- **Database Passwords**: ARANGO_PASSWORD, MONGO_PASSWORD, REDIS_PASSWORD, QDRANT_API_KEY
- **Public URLs**: FRONTEND_PUBLIC_URL, CONNECTOR_PUBLIC_BACKEND (for webhooks)
- **CORS Origins**: ALLOWED_ORIGINS for production deployment

### Development vs Production
- **Rate Limiting**: Automatically adjusts based on NODE_ENV (development: 1000/15min, production: 100/15min)
- **Error Responses**: Stack traces and detailed errors only in development mode
- **Logging**: Structured logging with different verbosity levels

## Testing and Quality

### Node.js Testing
```bash
npm test                    # Run all Mocha + Chai tests
npm run lint               # ESLint with TypeScript support
npm run format             # Prettier code formatting
```

### Python Testing
```bash
# Testing framework: Add pytest when implementing new features
ruff check .               # Linting with Python 3.10 target
ruff format .              # Code formatting
```

### Frontend Testing
```bash
npm run lint               # ESLint for React/TypeScript
npm run fm:check           # Prettier formatting check
# Testing framework: Consider adding Vitest for unit tests
```

## Deployment Architecture

### Single Container Approach
- **Multi-Process**: All services run in one Docker container managed by supervisord
- **Architecture Support**: ARM64 (Apple Silicon) and x86_64 with conditional npm install handling
- **Pre-installed Models**: HuggingFace embeddings, NLTK data, spaCy models baked into image
- **Persistent Storage**: Named Docker volumes for databases and application data

### Production Considerations
- **Security**: Strong database passwords, proper CORS origins, SSL/TLS termination
- **Monitoring**: Health checks for Qdrant and MongoDB with retry logic
- **Scaling**: Consider separating services for independent scaling
- **Resource Monitoring**: Vector operations are memory-intensive, monitor usage

## Key File Locations

### Configuration and Infrastructure
- `deployment/docker-compose/docker-compose.dev.yml` - Development services configuration
- `deployment/docker-compose/env.template` - Environment variables template
- `Dockerfile` - Multi-stage build with Python + Node.js runtime

### Backend Architecture
- `backend/nodejs/apps/src/app.ts` - Express application setup, middleware, rate limiting
- `backend/nodejs/apps/src/libs/types/container.types.ts` - InversifyJS dependency injection
- `backend/nodejs/apps/src/libs/middlewares/` - Authentication, error handling, CORS middleware

### Python Services
- `backend/python/app/query_main.py` - LangGraph-based Q&A workflows
- `backend/python/app/indexing_main.py` - Document processing and vectorization
- `backend/python/app/connectors_main.py` - External data source integration
- `backend/python/pyproject.toml` - Python dependencies and build configuration

### Frontend Structure
- `frontend/src/sections/` - Feature-specific UI components (auth, chat, knowledge base)
- `frontend/src/components/` - Reusable UI components with Material-UI theming
- `frontend/src/theme/` - Design system with 6 color schemes and responsive typography
- `frontend/design.md` - Comprehensive design system documentation

## Troubleshooting Common Issues

### Rate Limiting Errors (HTTP 429)
- Check if rate limit is too restrictive for development (should be 1000/15min in dev mode)
- Verify NODE_ENV is set to 'development' in container environment
- Restart pipeshub-ai container after code changes to rate limiting

### Service Communication Issues
- Verify all services are healthy: `docker compose ps`
- Check service discovery environment variables in docker-compose.dev.yml
- Ensure JWT secret synchronization between Node.js and Python services via ETCD

### Configuration Management Problems
- ETCD connection issues prevent service startup - check ETCD_URL and service health
- Encrypted configuration requires correct SECRET_KEY - verify environment variable
- Cache invalidation may be needed for configuration changes - restart affected services

### Vector Search Performance
- Qdrant operations are memory-intensive - monitor container resource usage
- Permission filtering affects search performance - ensure proper virtual record ID indexing
- Hybrid search combines dense + sparse results - verify both embedding models are loaded