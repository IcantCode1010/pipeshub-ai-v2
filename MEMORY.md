# PipesHub AI - Project Memory

## Project Overview
PipesHub AI is an enterprise workplace AI platform that provides unified natural language search and AI-powered question-answering across distributed workplace data sources. The platform uses microservices architecture with knowledge graph foundations and vector-based semantic search.

## Recent Issues Fixed

### 1. Security Vulnerabilities (Fixed: 2025-01-16)
**Problem**: Three critical security issues identified and resolved:

1. **Overly Permissive CORS Configuration**
   - Files: `backend/python/app/connectors_main.py`, `backend/python/app/query_main.py`
   - Issue: Wildcard CORS origins (`allow_origins=["*"]`) with credentials enabled
   - Fix: Replaced with specific allowed origins for dev and production
   - Impact: Prevents CSRF attacks and unauthorized access

2. **Insecure Package Dependency**
   - File: `backend/nodejs/apps/package.json`
   - Issue: Using security placeholder `"msal-node": "^0.0.1-security"`
   - Fix: Replaced with proper Azure MSAL package `"@azure/msal-node": "^2.16.2"`
   - Impact: Ensures proper Microsoft authentication functionality

3. **Missing Rate Limiting Protection**
   - Files: `backend/nodejs/apps/src/app.ts`, user management routes
   - Issue: No rate limiting despite TODO comments
   - Fix: Added express-rate-limit middleware (100 requests per 15 minutes per IP)
   - Impact: Protects against brute force attacks and API abuse

### 2. TypeScript Configuration Issue (Fixed: 2025-01-16)
**Problem**: TypeScript error "Cannot find type definition file for 'reflect-metadata'"
- File: `backend/nodejs/apps/tsconfig.json`
- Issue: Incorrect `"types": ["reflect-metadata"]` configuration
- Fix: Removed from types array (already properly imported in index.ts)
- Impact: TypeScript compilation now works without errors

## Architecture Summary

### Core Services
- **Node.js API Gateway** (port 3000): Authentication, user management, storage
- **Python Query Service** (port 8000): Semantic search, AI Q&A with LangGraph
- **Python Indexing Service** (port 8091): Document processing, vectorization
- **Python Connector Service** (port 8088): Data ingestion from external sources

### Data Storage
- **ArangoDB**: Knowledge graph database
- **Qdrant**: Vector database for embeddings
- **MongoDB**: Document storage
- **Redis**: Caching and task queuing
- **Kafka**: Event streaming
- **ETCD**: Configuration management

### AI/ML Stack
- **LangGraph**: Multi-agent workflows
- **LangChain**: LLM orchestration
- **Supported LLMs**: OpenAI, Anthropic, Gemini, AWS Bedrock, Ollama
- **Embeddings**: Multiple providers supported

## Development Environment

### Current Status
- Docker Compose deployment is the primary development method
- All services run in single container for development
- TypeScript compilation working properly
- Rate limiting implemented globally
- CORS configured securely

### Known Working Commands
```bash
# Docker Compose Development
cd deployment/docker-compose
docker compose -f docker-compose.dev.yml -p pipeshub-ai up --build -d

# Node.js Backend
cd backend/nodejs/apps
npm install
npm run build
npm run dev

# Python Services
cd backend/python
pip install -e .
python app/query_main.py      # Port 8000
python app/indexing_main.py   # Port 8091
python app/connectors_main.py # Port 8088

# Frontend
cd frontend
yarn install
yarn dev
```

## Security Improvements Made

### CORS Configuration
- Replaced wildcard origins with specific allowed domains
- Configured secure headers and methods
- Maintains credentials support for authenticated requests

### Rate Limiting
- 100 requests per 15 minutes per IP address
- Proper error handling and logging
- Applied globally to all routes

### Package Security
- Replaced security placeholder packages with proper implementations
- Updated dependencies to secure versions

## Current Dependencies Status

### Node.js Backend
- All packages installed and working
- TypeScript compilation successful
- Rate limiting middleware added (express-rate-limit v7.1.5)
- Proper MSAL package installed (@azure/msal-node v2.16.2)

### Python Services
- FastAPI-based microservices
- LangGraph for AI workflows
- Secure CORS configuration implemented

### Frontend
- React 18 with TypeScript
- Material-UI components
- Vite build system

## Configuration Notes

### Environment Variables Required
- Database URLs (ARANGO_URL, MONGO_URI, REDIS_URL, QDRANT_HOST)
- Authentication secrets (SECRET_KEY, JWT config)
- AI model API keys (OpenAI, Anthropic, etc.)
- External service credentials (Google OAuth, etc.)
- CORS origins for production deployment

### Port Mapping
- 3000: Frontend and Node.js API Gateway
- 8000: Python Query Service
- 8088: Python Connector Service
- 8091: Python Indexing Service
- 6333/6334: Qdrant vector database
- 8529: ArangoDB
- 27017: MongoDB
- 6379: Redis
- 9092: Kafka

## Future Considerations

### Security
- Regularly update CORS origins for production deployments
- Monitor rate limiting effectiveness
- Keep dependencies updated for security patches

### Performance
- Consider implementing service-specific rate limiting
- Monitor vector database performance
- Optimize LangGraph workflows for better response times

### Scalability
- Plan for horizontal scaling of individual services
- Consider service mesh implementation
- Implement proper monitoring and logging

## Documentation Status
- CLAUDE.md created and updated with latest fixes
- README.md contains deployment instructions
- Security improvements documented
- TypeScript configuration issues resolved

## Standalone Frontend (Added: 2025-01-19)

### Overview
A separate frontend application located at `standalone-frontend/` that runs on port 3001. This is an independent React/TypeScript application built with Vite.

### Technology Stack
- **React 18.3.1** with TypeScript
- **Material-UI v5** for components
- **Vite** as build tool
- **Redux Toolkit** for state management
- **React Router v6** for navigation
- **@iconify/react** for icons
- **Emotion** for styling
- **i18next** for internationalization
- **React Hook Form** with Zod for form validation

### Key Features
- Multi-language support (English, Arabic, Chinese, French, Vietnamese)
- JWT authentication with OAuth support (Google, Microsoft, SAML)
- Knowledge base search and browsing
- Q&A chatbot interface with PDF highlighting
- User and group management
- Organization profile management
- AI model configuration
- Service health monitoring

### Recent TypeScript Fixes (2025-01-19)

#### Issue 1: Incorrect Iconify Import Paths
**Problem**: Import statements using `@iconify/icons-mdi/` instead of `@iconify-icons/mdi/`
**Files Fixed**:
- `src/components/chat/chat-wrapper.tsx`
- `src/components/fallback/fallback-chat.tsx`
- `src/components/system-status/system-status-banner.tsx`

**Fix Applied**: Changed all imports from:
```typescript
import iconName from '@iconify/icons-mdi/icon-name';
```
to:
```typescript
import iconName from '@iconify-icons/mdi/icon-name';
```

#### Issue 2: Type Errors in Health Monitor Service
**Problem**: Type mismatches in `src/services/health-monitor.ts`
1. `overallStatus: 'checking'` - 'checking' is not a valid value for overallStatus type
2. String literal types not properly cast to union types

**Fix Applied**:
1. Changed initial `overallStatus` from `'checking'` to `'down' as const`
2. Added proper type assertions for status values:
   ```typescript
   status: (isHealthy ? 'healthy' : 'unhealthy') as 'healthy' | 'unhealthy'
   status: status as 'healthy' | 'unhealthy' | 'checking'
   ```

### Development Commands
```bash
cd standalone-frontend
npm install          # Install dependencies
npm run dev          # Start dev server on port 3001
npm run build        # Production build
npm run lint         # Run ESLint
npm run lint:fix     # Fix linting issues
npm run fm:check     # Check Prettier formatting
npm run fm:fix       # Fix formatting
```

### Project Structure
```
standalone-frontend/
├── src/
│   ├── app.tsx                 # Main app component
│   ├── auth/                   # Authentication components
│   ├── components/             # Reusable UI components
│   ├── context/               # React contexts
│   ├── hooks/                 # Custom React hooks
│   ├── layouts/               # Page layouts
│   ├── locales/               # i18n translations
│   ├── pages/                 # Route pages
│   ├── routes/                # Routing configuration
│   ├── sections/              # Feature-specific sections
│   ├── services/              # API services
│   ├── store/                 # Redux store
│   ├── theme/                 # MUI theme configuration
│   └── utils/                 # Utility functions
├── public/                    # Static assets
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
└── vite.config.ts            # Vite configuration
```

### Health Monitoring System
The standalone frontend includes a comprehensive health monitoring system that checks the status of all backend services:
- Backend API (port 3000)
- Query Service (port 8001)
- Indexing Service (port 8091)
- Connector Service (port 8088)
- ArangoDB (port 8529)
- Qdrant (port 6333)
- MongoDB (port 27017)
- Redis (port 6379)

The system provides:
- Real-time health checks every 30 seconds
- Visual status indicators
- Fallback UI when services are unavailable
- Detailed service status dialog

### Environment Configuration
The app uses Vite environment variables (configured in `.env` files):
- `VITE_BACKEND_URL`
- `VITE_QUERY_SERVICE_URL`
- `VITE_INDEXING_SERVICE_URL`
- `VITE_CONNECTOR_SERVICE_URL`
- `VITE_ARANGO_URL`
- `VITE_QDRANT_URL`
- `VITE_MONGODB_URL`
- `VITE_REDIS_URL`

## New User Registration System (Added: 2025-01-19)

### Overview
Implemented a comprehensive new user registration feature for the standalone frontend that integrates seamlessly with all backend services. The system provides a modern, multi-step registration flow with email verification and organization setup capabilities.

### Core Registration Features

#### 1. Enhanced Registration Form Component
**Location**: `src/auth/view/auth/user-registration.tsx`
- **Two-step wizard interface**: Account type selection followed by detailed user information
- **Account type support**: Individual (personal use) and Business (organization/team) accounts
- **Comprehensive validation**: Real-time form validation with Zod schema
- **Password strength indicator**: Visual 5-level strength meter with security requirements
- **Terms and privacy**: Required acceptance checkbox with policy links
- **Marketing consent**: Optional communication preferences
- **Responsive design**: Optimized for mobile and desktop experiences

#### 2. Backend Service Integration
**Location**: `src/auth/context/jwt/action.ts`
- **New `registerUser()` function**: Main registration API handler
- **Multi-step registration process**:
  1. User account creation via `/api/auth/sign-up`
  2. Organization setup via `/api/v1/org` (business accounts)
  3. Individual account setup (personal accounts)
  4. Welcome email delivery via `/api/v1/userAccount/welcome`
- **Comprehensive error handling**: Specific error messages for different failure scenarios
- **Account type differentiation**: Separate flows for individual vs business registrations

#### 3. Email Verification System
**Location**: `src/auth/view/auth/email-verification.tsx`
- **Token-based verification**: Secure email verification using URL tokens
- **Multiple verification states**: Verifying, success, error, and expired states
- **Resend functionality**: Users can request new verification emails
- **User-friendly messaging**: Clear instructions and status updates
- **Error recovery**: Options to resend emails or restart registration

#### 4. Enhanced Authentication Context
**Updated files**: `src/auth/types.ts`, `src/auth/context/jwt/auth-provider.tsx`
- **New `RegistrationData` type**: Strongly typed registration data structure
- **Enhanced auth context**: Added `register` function to existing authentication flow
- **Seamless integration**: Works with existing sign-in and session management

### Updated Routes and Navigation

#### New Authentication Routes
- **`/auth/sign-up`**: Main registration page with video background
- **`/auth/verify-email`**: Email verification page with token processing
- **`/auth/account-setup`**: Enhanced account setup for organizations
- **`/auth/reset-password`**: Password reset (existing, enhanced with video)

#### Enhanced User Experience
- **Video backgrounds**: All auth pages now use `Cockpit_Boot_Up_Video_Creation.mp4`
- **Navigation improvements**: Added "Create account" link on sign-in page
- **Consistent theming**: Unified design language across all auth flows

### Registration Flow Architecture

#### Complete User Journey
```
1. Sign-up Page → Account Type Selection (Individual/Business)
2. User Details Form → Validation & Password Strength Check
3. Terms Acceptance → Registration Submission
4. Success Message → Email Verification Instructions
5. Email Verification → Token Validation
6. Verified Account → Redirect to Sign-in
```

#### Account Types Supported
- **Individual Accounts**: Personal use with simplified setup
- **Business Accounts**: Organization creation with admin user assignment
- **Automatic role assignment**: Appropriate permissions based on account type

### Backend API Integration

#### Endpoint Utilization
- **`POST /api/auth/sign-up`**: Core user registration
- **`POST /api/v1/org`**: Organization and account setup
- **`POST /api/v1/userAccount/verify`**: Email verification processing
- **`POST /api/v1/userAccount/resend-verification`**: Verification email resending
- **`POST /api/v1/userAccount/welcome`**: Welcome email delivery

#### Error Handling Strategy
- **409 Conflict**: Account already exists handling
- **400 Bad Request**: Invalid data with specific error messages
- **500 Server Error**: Generic server error with retry options
- **Network errors**: Connection issue handling with retry capabilities

### Security Implementation

#### Password Requirements
- Minimum 8 characters with complexity requirements
- At least one uppercase letter, lowercase letter, number, and special character
- Real-time strength validation with visual feedback
- Confirmation field to prevent typos

#### Data Protection
- Secure token-based email verification
- Proper form validation to prevent malicious input
- Terms of service and privacy policy acceptance required
- Optional marketing consent with clear opt-out

### Technical Enhancements

#### TypeScript Integration
- Full type safety with zero compilation errors
- Strongly typed forms using Zod validation schemas
- Type-safe API integration with proper error handling
- Enhanced IDE support and development experience

#### Code Quality
- ESLint compliance with only minor style warnings
- Consistent code formatting and structure
- Comprehensive error boundaries and fallback states
- Modular component architecture for maintainability

### User Interface Improvements

#### Form Design
- **Material-UI v5** components with consistent theming
- **Multi-step wizard** with clear progress indication
- **Responsive layouts** that work on all screen sizes
- **Accessibility features** with proper ARIA labels and keyboard navigation

#### Visual Enhancements
- **Password strength meter** with color-coded feedback
- **Account type selection cards** with intuitive icons
- **Loading states** with progress indicators
- **Success/error messaging** with actionable next steps

### Integration with Existing Systems

#### Authentication Flow
- Seamless integration with existing JWT-based authentication
- Compatible with current session management
- Works with existing user roles and permissions
- Maintains backward compatibility with legacy auth methods

#### Database Integration
- Proper user record creation in existing user management system
- Organization setup using existing `AccountSetUp` flow
- Consistent data structure with current user models
- Maintains referential integrity across all services

## Last Updated
2025-01-19 - Implemented comprehensive new user registration system with email verification and enhanced authentication flows