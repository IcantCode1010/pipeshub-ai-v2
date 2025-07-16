# PipesHub AI - Complete File System Structure & Relationships

## Project Root Structure

```
pipeshub-ai/
├── README.md                           # Project overview, setup instructions, features
├── LICENSE                             # Open source license
├── CONTRIBUTING.md                     # Developer contribution guidelines
├── Dockerfile                          # Multi-stage Docker build for all services
├── backend/                            # Backend services (Node.js + Python)
├── frontend/                           # React frontend application
├── deployment/                         # Docker deployment configurations
└── docs/                              # Documentation files
```

---

## Backend Structure

### Node.js Backend (`backend/nodejs/`)

```
backend/nodejs/
├── apps/
│   ├── package.json                   # Node.js dependencies and scripts
│   ├── package-lock.json              # Locked dependency versions
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── Dockerfile                     # Node.js service containerization
│   ├── env.template                   # Environment variables template
│   │
│   └── src/                           # Source code
│       ├── index.ts                   # Application entry point
│       ├── app.ts                     # Express app setup, middleware, routing
│       │
│       ├── libs/                      # Shared libraries
│       │   ├── services/
│       │   │   └── logger.service.ts  # Centralized logging service
│       │   ├── middlewares/
│       │   │   ├── error.middleware.ts # Global error handling
│       │   │   └── request.context.ts  # Request context middleware
│       │   └── errors/
│       │       └── http.errors.ts     # HTTP error definitions
│       │
│       └── modules/                   # Feature modules
│           ├── auth/                  # Authentication & authorization
│           ├── user_management/       # User & organization management
│           ├── enterprise_search/     # Search orchestration
│           ├── knowledge_base/        # Document management
│           ├── configuration_manager/ # Config management
│           ├── storage/               # File storage
│           ├── tokens_manager/        # Token management
│           ├── mail/                  # Email services
│           ├── notification/          # Notification system
│           └── crawling_manager/      # Web crawling
```

#### Authentication Module (`src/modules/auth/`)

```
auth/
├── container/
│   └── authService.container.ts      # DI container for auth services
├── controller/
│   ├── userAccount.controller.ts     # Main auth controller (login, MFA, OAuth)
│   └── saml.controller.ts            # SAML SSO controller
├── middlewares/
│   ├── userAuthentication.middleware.ts # JWT validation, admin checks
│   └── types.ts                      # Middleware type definitions
├── routes/
│   ├── userAccount.routes.ts         # Auth API endpoints
│   ├── saml.routes.ts                # SAML SSO endpoints
│   └── orgAuthConfig.routes.ts       # Organization auth config
├── services/
│   ├── session.service.ts            # Redis session management
│   ├── auth.service.ts               # Core auth business logic
│   └── iam.service.ts                # Identity access management
├── utils/
│   ├── validateJwt.ts                # JWT token validation
│   ├── azureAdTokenValidation.ts     # Azure AD token validation
│   └── generateToken.ts              # Token generation utilities
└── schema/
    └── orgAuthConfiguration.schema.ts # Auth configuration schema
```

**Key Relationships:**
- `userAccount.controller.ts` → Orchestrates entire auth flow, calls session service
- `session.service.ts` → Redis for session storage, used by auth middleware
- `userAuthentication.middleware.ts` → Validates JWT tokens on protected routes
- `saml.controller.ts` → Handles SAML SSO callback, integrates with session service

#### User Management Module (`src/modules/user_management/`)

```
user_management/
├── container/
│   └── userManager.container.ts      # DI container setup
├── controller/
│   ├── users.controller.ts           # User CRUD operations
│   ├── userGroups.controller.ts      # User group management
│   └── org.controller.ts             # Organization management
├── routes/
│   ├── users.routes.ts               # User API endpoints
│   ├── userGroups.routes.ts          # Group API endpoints
│   └── org.routes.ts                 # Organization endpoints
├── services/
│   ├── users.service.ts              # User business logic
│   ├── userGroups.service.ts         # Group management logic
│   └── org.service.ts                # Organization logic
└── schema/
    ├── user.schema.ts                # User data validation
    ├── userGroup.schema.ts           # Group data validation
    └── org.schema.ts                 # Organization validation
```

**Key Relationships:**
- `users.controller.ts` → Called by auth module for user lookup
- `userGroups.service.ts` → Used by auth middleware for role validation
- `org.controller.ts` → Organization context for multi-tenancy

#### Configuration Manager Module (`src/modules/configuration_manager/`)

```
configuration_manager/
├── container/
│   └── cm.container.ts               # Configuration DI container
├── controller/
│   └── cm_controller.ts              # Config CRUD operations
├── routes/
│   └── cm_routes.ts                  # Configuration API endpoints
├── services/
│   └── cm.service.ts                 # Configuration business logic
├── config/
│   └── config.ts                     # Configuration loading
└── paths/
    └── paths.ts                      # Configuration path constants
```

**Key Relationships:**
- `cm.service.ts` → ETCD integration for distributed configuration
- Used by all modules for runtime configuration
- `paths.ts` → Defines configuration paths used across services

### Python Backend (`backend/python/`)

```
backend/python/
├── pyproject.toml                    # Python dependencies and project config
├── Dockerfile                        # Python services containerization
├── env.template                      # Environment variables template
├── cleanup_stuck_files.ps1           # Windows cleanup script
├── cleanup_stuck_files.sh            # Unix cleanup script
├── requirements.txt                  # Python dependencies (if used)
│
└── app/                              # Main application code
    ├── __init__.py                   # Package initialization
    ├── connectors_main.py            # Connector service entry point (port 8088)
    ├── indexing_main.py              # Indexing service entry point (port 8091)
    ├── query_main.py                 # Query service entry point (port 8000)
    │
    ├── api/                          # API layer
    │   ├── middlewares/
    │   │   └── auth.py               # Authentication middleware
    │   └── routes/                   # API route definitions
    │       ├── agent.py              # AI agent endpoints
    │       ├── chatbot.py            # Chat interface endpoints
    │       ├── health.py             # Health check endpoints
    │       ├── records.py            # Document record endpoints
    │       └── search.py             # Search endpoints
    │
    ├── builders/                     # Data builders
    │   ├── __init__.py
    │   └── records_builder.py        # Record construction logic
    │
    ├── config/                       # Configuration management
    │   ├── configuration_service.py  # Main config service
    │   ├── key_value_store.py        # KV store interface
    │   ├── key_value_store_factory.py # KV store factory
    │   ├── constants/
    │   │   └── __init__.py
    │   ├── encryption/
    │   │   └── __init__.py
    │   ├── providers/                # Config providers
    │   │   ├── etcd_provider.py      # ETCD configuration
    │   │   ├── file_provider.py      # File-based config
    │   │   └── memory_provider.py    # In-memory config
    │   └── utils/
    │       ├── config_utils.py       # Configuration utilities
    │       ├── named_constants/      # Named constants
    │       │   ├── arangodb_constants.py # ArangoDB constants
    │       │   └── http_status_code_constants.py # HTTP status codes
    │       └── validation/
    │           └── __init__.py
    │
    ├── connectors/                   # External data source connectors
    │   ├── api/
    │   │   ├── middleware.py         # Connector middleware
    │   │   ├── router.py             # Connector API routes
    │   │   └── webhook_handler.py    # Webhook handling
    │   ├── core/
    │   │   └── connector_factory/    # Connector factory pattern
    │   ├── services/
    │   │   ├── base_arango_service.py # Base ArangoDB service
    │   │   ├── connector_service.py  # Main connector service
    │   │   ├── entity_kafka_consumer.py # Kafka message consumer
    │   │   ├── google_token_handler.py # Google OAuth token handling
    │   │   └── sync_service.py       # Data synchronization
    │   ├── sources/                  # Specific connector implementations
    │   │   └── google/               # Google Workspace connectors
    │   │       ├── common/           # Shared Google utilities
    │   │       ├── drive/            # Google Drive connector
    │   │       └── gmail/            # Gmail connector
    │   └── utils/
    │       ├── connector_utils.py    # Connector utilities
    │       ├── permission_utils.py   # Permission mapping
    │       └── sync_utils.py         # Sync utilities
    │
    ├── core/                         # Core services
    │   ├── __init__.py
    │   ├── ai_arango_service.py      # AI-enhanced ArangoDB service
    │   ├── celery_app.py             # Celery task queue setup
    │   ├── arango_service.py         # ArangoDB service
    │   ├── logger.py                 # Logging configuration
    │   ├── llm_service.py            # LLM integration service
    │   └── signed_url.py             # Signed URL generation
    │
    ├── events/                       # Event handling
    │   ├── __init__.py
    │   ├── block_prompts.py          # Block-level prompts
    │   ├── events.py                 # Event definitions
    │   └── event_handlers.py         # Event processing
    │
    ├── exceptions/                   # Custom exceptions
    │   ├── embedding_exceptions.py   # Embedding-related errors
    │   ├── fastapi_responses.py      # FastAPI response errors
    │   └── indexing_exceptions.py    # Indexing-related errors
    │
    ├── models/                       # Data models
    │   ├── __init__.py
    │   ├── blocks.py                 # Content block models
    │   ├── file.py                   # File metadata models
    │   ├── graph.py                  # Graph data models
    │   ├── permission.py             # Permission models
    │   ├── records.py                # Document record models
    │   └── user.py                   # User models
    │
    ├── modules/                      # Feature modules
    │   ├── __init__.py
    │   ├── agents/                   # AI agent implementations
    │   │   └── conversational/       # Conversational agents
    │   ├── extraction/               # Metadata extraction
    │   │   ├── extraction_service.py # Main extraction service
    │   │   ├── metadata_extractor.py # Metadata extraction logic
    │   │   ├── prompt_template.py    # Extraction prompts
    │   │   └── README.md             # Extraction documentation
    │   ├── indexing/                 # Document indexing
    │   │   ├── indexing_service.py   # Main indexing service
    │   │   └── README.md             # Indexing documentation
    │   ├── ingestion/                # Data ingestion
    │   │   ├── ingestion_service.py  # Main ingestion service
    │   │   └── README.md             # Ingestion documentation
    │   ├── parsers/                  # Document parsers
    │   │   ├── base_parser.py        # Base parser interface
    │   │   ├── pdf_parser/           # PDF parsing
    │   │   ├── docx_parser/          # Word document parsing
    │   │   ├── xlsx_parser/          # Excel parsing
    │   │   ├── pptx_parser/          # PowerPoint parsing
    │   │   ├── html_parser/          # HTML parsing
    │   │   ├── text_parser/          # Plain text parsing
    │   │   ├── csv_parser/           # CSV parsing
    │   │   └── markdown_parser/      # Markdown parsing
    │   ├── qna/                      # Question & Answer
    │   │   └── prompt_templates.py   # Q&A prompt templates
    │   ├── reranker/                 # Result reranking
    │   │   └── reranker_service.py   # Reranking logic
    │   ├── retrieval/                # Document retrieval
    │   │   ├── retrieval_service.py  # Main retrieval service
    │   │   ├── retrieval_arango.py   # ArangoDB retrieval
    │   │   └── README.md             # Retrieval documentation
    │   └── streaming/                # Streaming responses
    │       ├── streaming_service.py  # Streaming logic
    │       └── sse_handler.py        # Server-sent events
    │
    ├── schema/                       # Database schemas
    │   └── arango/                   # ArangoDB schemas
    │       ├── documents.py          # Document schemas
    │       └── edges.py              # Edge/relationship schemas
    │
    ├── scripts/                      # Utility scripts
    │   └── services_linux.sh         # Linux service management
    │
    ├── services/                     # Business services
    │   ├── __init__.py
    │   ├── ai_config_handler.py      # AI configuration handling
    │   └── kafka_consumer.py         # Kafka message consumption
    │
    ├── setups/                       # Service initialization
    │   ├── connector_setup.py        # Connector service setup
    │   ├── indexing_setup.py         # Indexing service setup
    │   └── query_setup.py            # Query service setup
    │
    └── utils/                        # Utility functions
        ├── citations.py              # Citation handling
        ├── datetime_utils.py         # Date/time utilities
        ├── embeddings.py             # Embedding utilities
        ├── file_utils.py             # File operations
        ├── format_utils.py           # Data formatting
        ├── logging_utils.py          # Logging utilities
        ├── query_decompose.py        # Query decomposition
        ├── text_utils.py             # Text processing
        ├── time_conversion.py        # Time conversion utilities
        └── validation_utils.py       # Data validation
```

**Key Python Service Relationships:**

#### Query Service (`query_main.py`)
- **Purpose**: Handles search queries and AI-powered Q&A
- **Port**: 8000
- **Dependencies**: 
  - `modules/retrieval/` → Document search and retrieval
  - `modules/qna/` → Answer generation with LLMs
  - `core/llm_service.py` → LLM integration
  - `utils/query_decompose.py` → Complex query analysis

#### Connector Service (`connectors_main.py`)
- **Purpose**: Integrates with external data sources
- **Port**: 8088
- **Dependencies**:
  - `connectors/sources/google/` → Google Workspace integration
  - `connectors/services/sync_service.py` → Data synchronization
  - `core/celery_app.py` → Background task processing

#### Indexing Service (`indexing_main.py`)
- **Purpose**: Processes and indexes documents
- **Port**: 8091
- **Dependencies**:
  - `modules/parsers/` → Document parsing
  - `modules/extraction/` → Metadata extraction
  - `modules/indexing/` → Vector indexing
  - `utils/embeddings.py` → Embedding generation

---

## Frontend Structure (`frontend/`)

```
frontend/
├── package.json                      # Frontend dependencies and scripts
├── package-lock.json                 # Locked dependency versions
├── tsconfig.json                     # TypeScript configuration
├── vite.config.ts                    # Vite build configuration
├── index.html                        # Main HTML template
├── Dockerfile                        # Frontend containerization
├── env.template                      # Environment variables template
├── tailwind.config.js                # Tailwind CSS configuration
├── eslint.config.js                  # ESLint configuration
├── prettier.config.js                # Prettier configuration
│
├── public/                           # Static assets
│   ├── favicon.ico                   # Website favicon
│   ├── assets/                       # Static assets
│   │   ├── icons/                    # Icon collections
│   │   │   ├── home/                 # Home page icons
│   │   │   ├── navbar/               # Navigation icons
│   │   │   ├── notification/         # Notification icons
│   │   │   └── platforms/            # Platform icons
│   │   └── illustrations/            # Illustration assets
│   ├── fonts/                        # Custom fonts
│   │   ├── Roboto-Bold.ttf
│   │   └── Roboto-Regular.ttf
│   └── logo/                         # Logo assets
│       ├── logo-blue.svg
│       ├── logo-full.svg
│       └── logo-single.jpg
│
├── packages/                         # Local packages
│   └── xlsx-0.20.3.tgz              # Excel processing package
│
└── src/                              # Source code
    ├── main.tsx                      # Application entry point
    ├── app.tsx                       # Root application component
    ├── global.css                    # Global styles
    ├── config-global.ts              # Global configuration
    │
    ├── actions/                      # Action creators
    │   └── chat.ts                   # Chat-related actions
    │
    ├── assets/                       # Asset management
    │   └── data/
    │       ├── countries.ts          # Country data
    │       └── index.ts              # Asset exports
    │
    ├── auth/                         # Authentication system
    │   ├── components/               # Auth UI components
    │   │   ├── form-divider.tsx      # Form divider component
    │   │   ├── form-head.tsx         # Form header component
    │   │   ├── form-resend-code.tsx  # Resend code component
    │   │   ├── form-wrapper.tsx      # Form wrapper component
    │   │   ├── password-strength.tsx # Password strength indicator
    │   │   ├── sign-in-button.tsx    # Sign-in button component
    │   │   └── sign-up-terms.tsx     # Terms acceptance component
    │   ├── context/                  # Auth context providers
    │   │   ├── auth-context.tsx      # Main auth context
    │   │   └── jwt/                  # JWT authentication
    │   │       ├── auth-provider.tsx # JWT auth provider
    │   │       ├── auth-context.tsx  # JWT auth context
    │   │       ├── action.ts         # Auth actions
    │   │       ├── utils.ts          # Auth utilities
    │   │       └── types.ts          # Auth type definitions
    │   ├── guard/                    # Route protection
    │   │   ├── auth-guard.tsx        # Authentication guard
    │   │   ├── guest-guard.tsx       # Guest-only guard
    │   │   ├── admin-guard.tsx       # Admin access guard
    │   │   ├── account-type-guard.tsx # Account type guard
    │   │   ├── role-based-guard.tsx  # Role-based guard
    │   │   └── types.ts              # Guard type definitions
    │   ├── hooks/                    # Auth hooks
    │   │   ├── index.ts              # Hook exports
    │   │   └── use-auth-context.ts   # Auth context hook
    │   ├── styles/                   # Auth styles
    │   │   └── auth-styles.ts        # Authentication styles
    │   ├── types/                    # Auth types
    │   │   └── auth.ts               # Auth type definitions
    │   ├── types.ts                  # General auth types
    │   └── view/                     # Auth views
    │       ├── auth/                 # Authentication views
    │       │   ├── authentication-view.tsx # Main auth view
    │       │   ├── password-sign-in.tsx # Password login
    │       │   ├── otp-sign-in.tsx   # OTP verification
    │       │   ├── google-sign-in.tsx # Google OAuth
    │       │   ├── microsoft-sign-in.tsx # Microsoft OAuth
    │       │   ├── azure-sign-in.tsx # Azure AD OAuth
    │       │   ├── oauth-sign-in.tsx # Generic OAuth
    │       │   ├── oauth-callback.tsx # OAuth callback handler
    │       │   ├── saml-sign-in.tsx  # SAML SSO
    │       │   ├── forgot-password.tsx # Password reset
    │       │   ├── reset-password.tsx # Password reset form
    │       │   ├── verify-otp.tsx    # OTP verification
    │       │   └── types.ts          # View type definitions
    │       └── jwt/                  # JWT views
    │           └── sign-in-view.tsx  # JWT sign-in view
    │
    ├── components/                   # Reusable UI components
    │   ├── animate/                  # Animation components
    │   │   ├── motion-container.tsx  # Motion container
    │   │   ├── motion-lazy.tsx       # Lazy motion loading
    │   │   ├── motion-viewport.tsx   # Viewport animations
    │   │   ├── variants/             # Animation variants
    │   │   └── types.ts              # Animation types
    │   ├── carousel/                 # Carousel components
    │   │   ├── carousel.tsx          # Main carousel
    │   │   ├── carousel-dots.tsx     # Carousel dots
    │   │   ├── carousel-arrows.tsx   # Carousel arrows
    │   │   └── types.ts              # Carousel types
    │   ├── chart/                    # Chart components
    │   │   ├── chart.tsx             # Main chart component
    │   │   ├── use-chart.ts          # Chart hook
    │   │   └── types.ts              # Chart types
    │   ├── custom-breadcrumbs/       # Breadcrumb navigation
    │   │   ├── custom-breadcrumbs.tsx # Main breadcrumbs
    │   │   └── types.ts              # Breadcrumb types
    │   ├── custom-dialog/            # Dialog components
    │   │   ├── custom-dialog.tsx     # Main dialog
    │   │   └── types.ts              # Dialog types
    │   ├── custom-popover/           # Popover components
    │   │   ├── custom-popover.tsx    # Main popover
    │   │   ├── use-popover.ts        # Popover hook
    │   │   └── types.ts              # Popover types
    │   ├── editor/                   # Rich text editor
    │   │   ├── editor.tsx            # Main editor
    │   │   ├── toolbar/              # Editor toolbar
    │   │   └── types.ts              # Editor types
    │   ├── hook-form/                # Form components
    │   │   ├── rhf-text-field.tsx    # Text field
    │   │   ├── rhf-select.tsx        # Select field
    │   │   ├── rhf-checkbox.tsx      # Checkbox field
    │   │   └── [other form fields]   # Various form fields
    │   ├── iconify/                  # Icon components
    │   │   ├── iconify.tsx           # Main icon component
    │   │   └── types.ts              # Icon types
    │   ├── loading-screen/           # Loading components
    │   │   ├── loading-screen.tsx    # Main loading screen
    │   │   ├── splash-screen.tsx     # Splash screen
    │   │   └── types.ts              # Loading types
    │   ├── logo/                     # Logo components
    │   │   ├── logo.tsx              # Main logo component
    │   │   └── types.ts              # Logo types
    │   ├── settings/                 # Settings components
    │   │   ├── settings-drawer.tsx   # Settings drawer
    │   │   ├── settings-provider.tsx # Settings provider
    │   │   └── types.ts              # Settings types
    │   ├── snackbar/                 # Notification components
    │   │   ├── snackbar.tsx          # Main snackbar
    │   │   └── types.ts              # Snackbar types
    │   └── table/                    # Table components
    │       ├── table.tsx             # Main table
    │       ├── table-pagination.tsx  # Table pagination
    │       └── types.ts              # Table types
    │
    ├── context/                      # React contexts
    │   ├── AdminContext.tsx          # Admin context
    │   ├── GroupsContext.tsx         # Groups context
    │   └── UserContext.tsx           # User context
    │
    ├── hooks/                        # Custom React hooks
    │   ├── use-boolean.ts            # Boolean state hook
    │   ├── use-client-rect.ts        # Client rect hook
    │   ├── use-copy-to-clipboard.ts  # Clipboard hook
    │   ├── use-debounce.ts           # Debounce hook
    │   ├── use-local-storage.ts      # Local storage hook
    │   ├── use-responsive.ts         # Responsive hook
    │   ├── use-router.ts             # Router hook
    │   ├── use-scroll-to-top.ts      # Scroll to top hook
    │   ├── use-set-state.ts          # Set state hook
    │   ├── use-tabs.ts               # Tabs hook
    │   ├── use-table.ts              # Table hook
    │   └── use-websocket.ts          # WebSocket hook
    │
    ├── layouts/                      # Layout components
    │   ├── auth-centered/            # Centered auth layout
    │   │   ├── layout.tsx            # Main layout
    │   │   ├── section.tsx           # Layout section
    │   │   └── types.ts              # Layout types
    │   ├── auth-split/               # Split auth layout
    │   │   ├── layout.tsx            # Main layout
    │   │   ├── section.tsx           # Layout section
    │   │   └── types.ts              # Layout types
    │   ├── dashboard/                # Dashboard layout
    │   │   ├── layout.tsx            # Main dashboard layout
    │   │   ├── header.tsx            # Dashboard header
    │   │   ├── nav-vertical.tsx      # Vertical navigation
    │   │   ├── nav-horizontal.tsx    # Horizontal navigation
    │   │   ├── nav-mini.tsx          # Mini navigation
    │   │   ├── main.tsx              # Main content area
    │   │   └── types.ts              # Dashboard types
    │   ├── components/               # Layout components
    │   │   ├── header-simple.tsx     # Simple header
    │   │   ├── nav-toggle-button.tsx # Navigation toggle
    │   │   ├── searchbar.tsx         # Search bar
    │   │   ├── settings-button.tsx   # Settings button
    │   │   ├── account-popover.tsx   # Account popover
    │   │   ├── contacts-popover.tsx  # Contacts popover
    │   │   ├── notifications-popover.tsx # Notifications popover
    │   │   ├── language-popover.tsx  # Language selector
    │   │   ├── workspaces-popover.tsx # Workspace selector
    │   │   └── nav-upgrade.tsx       # Navigation upgrade
    │   ├── config-nav-account.tsx    # Account navigation config
    │   ├── config-nav-dashboard.tsx  # Dashboard navigation config
    │   └── classes.ts                # Layout CSS classes
    │
    ├── locales/                      # Internationalization
    │   ├── all-langs.ts              # All language definitions
    │   ├── config-locales.ts         # Locale configuration
    │   ├── i18n-provider.tsx         # i18n provider
    │   ├── localization-provider.tsx # Localization provider
    │   ├── use-locales.ts            # Locales hook
    │   ├── langs/                    # Language files
    │   │   ├── en/                   # English translations
    │   │   ├── fr/                   # French translations
    │   │   ├── vi/                   # Vietnamese translations
    │   │   ├── cn/                   # Chinese translations
    │   │   └── ar/                   # Arabic translations
    │   └── utils/
    │       └── highlight.ts          # Text highlighting
    │
    ├── pages/                        # Page components
    │   ├── auth/                     # Authentication pages
    │   │   └── jwt/                  # JWT auth pages
    │   │       └── sign-in.tsx       # Sign-in page
    │   ├── dashboard/                # Dashboard pages
    │   │   ├── app.tsx               # Main app page
    │   │   ├── analytics.tsx         # Analytics page
    │   │   ├── ecommerce.tsx         # E-commerce page
    │   │   ├── banking.tsx           # Banking page
    │   │   └── booking.tsx           # Booking page
    │   ├── error/                    # Error pages
    │   │   ├── 403.tsx               # Forbidden page
    │   │   ├── 404.tsx               # Not found page
    │   │   └── 500.tsx               # Server error page
    │   └── maintenance/              # Maintenance pages
    │       └── maintenance.tsx       # Maintenance page
    │
    ├── routes/                       # Routing system
    │   ├── components/               # Route components
    │   │   ├── router-link.tsx       # Router link component
    │   │   └── types.ts              # Route types
    │   ├── hooks/                    # Route hooks
    │   │   ├── use-active-link.ts    # Active link hook
    │   │   ├── use-pathname.ts       # Pathname hook
    │   │   ├── use-params.ts         # Params hook
    │   │   ├── use-router.ts         # Router hook
    │   │   ├── use-search-params.ts  # Search params hook
    │   │   └── types.ts              # Hook types
    │   ├── sections/                 # Route sections
    │   │   ├── auth.tsx              # Auth routes
    │   │   ├── dashboard.tsx         # Dashboard routes
    │   │   ├── error.tsx             # Error routes
    │   │   └── main.tsx              # Main routes
    │   ├── paths.ts                  # Route path constants
    │   └── utils.ts                  # Route utilities
    │
    ├── sections/                     # Feature sections
    │   ├── accountdetails/           # Account details section
    │   │   ├── account-details-view.tsx # Account details view
    │   │   ├── account-general.tsx   # General account info
    │   │   ├── account-billing.tsx   # Billing information
    │   │   ├── account-security.tsx  # Security settings
    │   │   ├── account-notifications.tsx # Notification settings
    │   │   └── components/           # Account components
    │   │       ├── account-change-password.tsx # Password change
    │   │       ├── account-delete.tsx # Account deletion
    │   │       ├── account-social-links.tsx # Social links
    │   │       └── authentication-settings.tsx # Auth settings
    │   ├── knowledgebase/            # Knowledge base section
    │   │   ├── knowledge-base-view.tsx # Main KB view
    │   │   ├── knowledge-base-list.tsx # KB list view
    │   │   ├── knowledge-base-details.tsx # KB details
    │   │   ├── knowledge-base-create.tsx # KB creation
    │   │   ├── knowledge-base-edit.tsx # KB editing
    │   │   ├── knowledge-base-filters.tsx # KB filters
    │   │   ├── knowledge-base-search.tsx # KB search
    │   │   ├── knowledge-base-table.tsx # KB table
    │   │   ├── knowledge-base-table-row.tsx # KB table row
    │   │   ├── knowledge-base-table-toolbar.tsx # KB toolbar
    │   │   ├── knowledge-base-quick-edit-form.tsx # Quick edit
    │   │   ├── knowledge-base-new-edit-form.tsx # New/edit form
    │   │   └── components/           # KB components
    │   │       ├── connector-status.tsx # Connector status
    │   │       └── indexing-progress.tsx # Indexing progress
    │   ├── qna/                      # Q&A section
    │   │   ├── chatbot/              # Chatbot interface
    │   │   │   ├── chat-bot.tsx      # Main chat interface
    │   │   │   ├── chat-header.tsx   # Chat header
    │   │   │   ├── chat-input.tsx    # Chat input field
    │   │   │   ├── chat-message.tsx  # Chat message component
    │   │   │   ├── chat-sidebar.tsx  # Chat sidebar
    │   │   │   └── components/       # Chat components
    │   │   │       ├── citations-hover-card.tsx # Citations display
    │   │   │       ├── message-actions.tsx # Message actions
    │   │   │       ├── typing-indicator.tsx # Typing indicator
    │   │   │       └── dialogs/      # Chat dialogs
    │   │   │           ├── share-conversation-dialog.tsx # Share dialog
    │   │   │           └── delete-conversation-dialog.tsx # Delete dialog
    │   │   ├── search/               # Search interface
    │   │   │   ├── search-view.tsx   # Main search view
    │   │   │   ├── search-input.tsx  # Search input
    │   │   │   ├── search-results.tsx # Search results
    │   │   │   └── search-filters.tsx # Search filters
    │   │   └── analytics/            # Q&A analytics
    │   │       ├── analytics-view.tsx # Analytics view
    │   │       └── analytics-charts.tsx # Analytics charts
    │   ├── error/                    # Error sections
    │   │   ├── 403-view.tsx          # 403 error view
    │   │   ├── 404-view.tsx          # 404 error view
    │   │   ├── 500-view.tsx          # 500 error view
    │   │   └── types.ts              # Error types
    │   ├── maintenance/              # Maintenance sections
    │   │   └── maintenance-view.tsx  # Maintenance view
    │   ├── permission/               # Permission sections
    │   │   └── view.tsx              # Permission view
    │   └── coming-soon/              # Coming soon sections
    │       └── coming-soon-view.tsx  # Coming soon view
    │
    ├── store/                        # Redux store
    │   ├── store.ts                  # Main store configuration
    │   ├── authSlice.ts              # Authentication slice
    │   └── userAndGroupsSlice.ts     # User and groups slice
    │
    ├── theme/                        # Theme configuration
    │   ├── create-theme.ts           # Theme creation
    │   ├── overrides-theme.ts        # Theme overrides
    │   ├── scheme-config.ts          # Color scheme config
    │   ├── theme-provider.tsx        # Theme provider
    │   ├── core/                     # Core theme files
    │   │   ├── palette.ts            # Color palette
    │   │   ├── typography.ts         # Typography settings
    │   │   ├── shadows.ts            # Shadow definitions
    │   │   ├── components.ts         # Component overrides
    │   │   ├── mixins.ts             # CSS mixins
    │   │   ├── breakpoints.ts        # Responsive breakpoints
    │   │   └── options/              # Theme options
    │   │       └── presets.ts        # Theme presets
    │   ├── styles/                   # Style utilities
    │   │   ├── global.ts             # Global styles
    │   │   ├── reset.ts              # CSS reset
    │   │   └── scrollbar.ts          # Scrollbar styles
    │   └── with-settings/            # Theme with settings
    │       ├── settings-provider.tsx # Settings provider
    │       ├── settings-drawer.tsx   # Settings drawer
    │       └── default-settings.ts   # Default settings
    │
    ├── types/                        # TypeScript type definitions
    │   ├── auth.ts                   # Authentication types
    │   ├── blog.ts                   # Blog types
    │   ├── calendar.ts               # Calendar types
    │   ├── chat-bot.ts               # Chatbot types
    │   ├── chat-sidebar.ts           # Chat sidebar types
    │   ├── file.ts                   # File types
    │   ├── kanban.ts                 # Kanban types
    │   ├── mail.ts                   # Mail types
    │   └── user.ts                   # User types
    │
    └── utils/                        # Utility functions
        ├── axios.tsx                 # HTTP client configuration
        ├── change-case.ts            # Text case conversion
        ├── format-number.ts          # Number formatting
        ├── format-time.ts            # Time formatting
        ├── highlight.ts              # Text highlighting
        ├── storage-available.ts      # Storage availability check
        └── uuidv4.ts                 # UUID generation
```

**Key Frontend Relationships:**

#### Main Application Flow
- `main.tsx` → `app.tsx` → All providers and routing
- `auth/context/jwt/auth-provider.tsx` → Manages global auth state
- `routes/sections/` → Route definitions connecting to page components
- `layouts/dashboard/` → Main application layout wrapping all pages

#### Authentication Flow
- `auth/view/auth/authentication-view.tsx` → Orchestrates login flow
- `auth/context/jwt/action.ts` → API calls to Node.js backend
- `auth/guard/auth-guard.tsx` → Protects routes requiring authentication
- `store/authSlice.ts` → Redux state management for auth

#### Chat Interface
- `sections/qna/chatbot/chat-bot.tsx` → Main chat interface
- `sections/qna/chatbot/components/citations-hover-card.tsx` → Citation display
- `utils/axios.tsx` → API communication with Python query service
- `hooks/use-websocket.ts` → Real-time communication

---

## Deployment Structure (`deployment/`)

```
deployment/
├── docker-compose/
│   ├── docker-compose.dev.yml        # Development environment
│   ├── docker-compose.prod.yml       # Production environment
│   ├── docker-compose.ollama-dev.yml # Development with Ollama
│   ├── env.template                  # Environment variables template
│   ├── README.md                     # Deployment documentation
│   └── scripts/
│       └── start-ollama.sh           # Ollama startup script
└── kubernetes/                       # Kubernetes manifests (future)
```

**Deployment Relationships:**
- `docker-compose.dev.yml` → Builds from local source, development settings
- `docker-compose.prod.yml` → Uses pre-built images, production optimizations
- `docker-compose.ollama-dev.yml` → Includes local LLM support
- `env.template` → Environment variables used by all services

---

## Documentation (`docs/`)

```
docs/
└── README.md                         # Additional documentation
```

---

## Key Cross-Service Relationships

### 1. Authentication Flow
```
Frontend (auth-provider.tsx) 
  ↓ JWT token request
Node.js (userAccount.controller.ts)
  ↓ User validation
MongoDB (user collections)
  ↓ Session storage
Redis (session management)
  ↓ Auth middleware
Python services (auth.py middleware)
```

### 2. Chat/Search Flow
```
Frontend (chat-bot.tsx)
  ↓ Chat message
Node.js (enterprise_search routes)
  ↓ Query forwarding
Python Query Service (query_main.py)
  ↓ Document retrieval
Qdrant (vector search) + ArangoDB (metadata)
  ↓ LLM processing
OpenAI/Anthropic/Ollama
  ↓ Response with citations
Frontend (citations display)
```

### 3. Document Processing Flow
```
Frontend (knowledge-base upload)
  ↓ File upload
Node.js (storage service)
  ↓ Processing trigger
Python Indexing Service (indexing_main.py)
  ↓ Document parsing
Parsers (PDF, DOCX, etc.)
  ↓ Text extraction + embedding
AI Models (BAAI/bge-large-en-v1.5)
  ↓ Vector storage
Qdrant (embeddings) + ArangoDB (metadata)
```

### 4. Connector Sync Flow
```
External APIs (Google, Microsoft)
  ↓ Webhook/polling
Python Connector Service (connectors_main.py)
  ↓ Data extraction
Connector sources (google/, microsoft/)
  ↓ Permission mapping
ArangoDB (permissions + metadata)
  ↓ Indexing trigger
Kafka (message queue)
  ↓ Processing
Python Indexing Service
```

### 5. Configuration Management
```
ETCD (distributed config)
  ↓ Config retrieval
Node.js (configuration_manager)
  ↓ Config API
Frontend (settings pages)
  ↓ Runtime updates
All services (config consumption)
```

This comprehensive file system structure shows how each component fits into the larger PipesHub AI ecosystem, with clear relationships between frontend components, backend services, and infrastructure elements. The modular architecture enables independent development and deployment while maintaining strong integration points for seamless functionality.
