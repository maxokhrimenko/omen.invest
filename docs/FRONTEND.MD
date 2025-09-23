# 🎨 Frontend Documentation

## Table of Contents
- [1. Overview](#1-overview)
- [2. Architecture](#2-architecture)
- [3. Dependencies & Requirements](#3-dependencies--requirements)
- [4. File Structure & Relationships](#4-file-structure--relationships)
- [5. Core Components](#5-core-components)
- [6. State Management](#6-state-management)
- [7. API Integration](#7-api-integration)
- [8. Routing & Navigation](#8-routing--navigation)
- [9. Styling & Design System](#9-styling--design-system)
- [10. Error Handling](#10-error-handling)
- [11. Performance Optimizations](#11-performance-optimizations)
- [12. Logging & Monitoring](#12-logging--monitoring)
- [13. Testing](#13-testing)
- [14. Build & Deployment](#14-build--deployment)
- [15. Development Guidelines](#15-development-guidelines)

---

## 1. Overview

The frontend is a React-based portfolio analysis application built with TypeScript, providing a modern web interface for portfolio management, analysis, and administration. It features a clean, responsive design with comprehensive financial data visualization and real-time analysis capabilities.

**Key Features:**
- Portfolio upload and management with drag-and-drop CSV support
- Real-time portfolio analysis with comprehensive financial metrics
- Interactive charts and data visualization using Recharts
- Administration interface for system management
- Error boundary system with graceful error recovery
- Structured logging with backend correlation
- Toast notification system for user feedback
- Responsive design optimized for all devices

**Entry Points:**
- `frontend/src/main.tsx` - React application entry point
- `frontend/src/App.tsx` - Main application component with routing

---

## 2. Architecture

### Component Architecture

```
┌─────────────────────────────────────────┐
│              App Component              │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ ErrorBoundary│  │ ToastProvider   │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│            Router & Layout              │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ MainLayout  │  │ Sidebar         │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│              Pages                      │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Dashboard   │  │ PortfolioAnalysis│   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│            Components                   │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Portfolio   │  │ Charts & Metrics│   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│            Services & Hooks             │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ API Service │  │ Custom Hooks    │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
```

### Data Flow

```
User Action → Component → Hook → API Service → Backend
     ↓              ↓        ↓         ↓
UI Update ← State Update ← Response ← HTTP Response
```

---

## 3. Dependencies & Requirements

### Core Dependencies

| Package | Version | Purpose | Usage |
|---------|---------|---------|-------|
| `react` | ^19.1.1 | UI framework | Component library |
| `react-dom` | ^19.1.1 | DOM rendering | React DOM operations |
| `react-router-dom` | ^7.9.1 | Routing | Navigation and routing |
| `typescript` | ~5.8.3 | Type safety | Static type checking |

### UI & Styling

| Package | Version | Purpose | Usage |
|---------|---------|---------|-------|
| `tailwindcss` | ^3.4.0 | CSS framework | Utility-first styling |
| `lucide-react` | ^0.544.0 | Icons | Icon library |
| `recharts` | ^3.2.1 | Charts | Data visualization |

### Data & API

| Package | Version | Purpose | Usage |
|---------|---------|---------|-------|
| `axios` | ^1.12.2 | HTTP client | API communication |
| `react-dropzone` | ^14.3.8 | File upload | Drag-and-drop file handling |

### Development Tools

| Package | Version | Purpose | Usage |
|---------|---------|---------|-------|
| `vite` | ^7.1.6 | Build tool | Development server and bundling |
| `@vitejs/plugin-react` | ^5.0.2 | Vite plugin | React support |
| `eslint` | ^9.35.0 | Linting | Code quality |
| `typescript-eslint` | ^8.43.0 | TypeScript linting | TypeScript code quality |

---

## 4. File Structure & Relationships

### Directory Structure

```
frontend/
├── public/                        # Static assets
│   ├── android-chrome-*.png       # PWA icons
│   ├── apple-touch-icon.png       # Apple touch icon
│   ├── favicon-*.png              # Favicon files
│   ├── logo.png                   # Application logo
│   └── vite.svg                   # Vite logo
├── src/                           # Source code
│   ├── components/                # React components
│   │   ├── common/                # Common UI components
│   │   ├── portfolio/             # Portfolio-specific components
│   │   │   ├── PortfolioTable.tsx             # Portfolio data table
│   │   │   ├── PortfolioUpload.tsx            # File upload component
│   │   │   ├── PortfolioChart.tsx             # Performance charts
│   │   │   ├── PortfolioMetrics.tsx           # Metrics display
│   │   │   ├── RedesignedPortfolioMetrics.tsx # Enhanced metrics
│   │   │   ├── PortfolioMetricsCompact.tsx    # Compact metrics view
│   │   │   ├── PortfolioMetricsDisplay.tsx    # Metrics display wrapper
│   │   │   ├── MetricsLegend.tsx              # Color coding legend
│   │   │   ├── AnalysisTrigger.tsx            # Analysis button
│   │   │   ├── DataAvailabilityWarnings.tsx   # Data warnings
│   │   │   ├── DateRangeSelector.tsx          # Date range picker
│   │   │   ├── TickerAnalysisDisplay.tsx      # Individual ticker analysis
│   │   │   ├── TickerMetricsTable.tsx         # Ticker metrics table
│   │   │   ├── TickerMetricsCard.tsx          # Ticker metrics card
│   │   │   ├── TickerMetricsGrid.tsx          # Ticker metrics grid
│   │   │   ├── TickerComparisonTable.tsx      # Ticker comparison
│   │   │   └── TickerComparisonCard.tsx       # Ticker comparison card
│   │   ├── ErrorBoundary.tsx      # Error boundary component
│   │   └── Logo.tsx               # Application logo
│   ├── contexts/                  # React contexts
│   │   └── ToastContext.tsx       # Toast notification context
│   ├── hooks/                     # Custom React hooks
│   │   └── usePortfolioAnalysis.ts # Portfolio analysis hook
│   ├── pages/                     # Page components
│   │   ├── DashboardPage.tsx      # Main dashboard
│   │   ├── PortfolioAnalysisPage.tsx # Portfolio analysis page
│   │   ├── PortfolioUploadPage.tsx # Portfolio upload page
│   │   └── AdministrationPage.tsx # Administration interface
│   ├── services/                  # API services
│   │   └── api.ts                 # API service with axios
│   ├── types/                     # TypeScript type definitions
│   │   ├── api.ts                 # API types
│   │   └── portfolio.ts           # Portfolio types
│   ├── utils/                     # Utility functions
│   │   ├── logger.ts              # Frontend logging service
│   │   └── timeoutCalculator.ts   # Timeout calculations
│   ├── App.tsx                    # Main application component
│   ├── main.tsx                   # Application entry point
│   ├── App.css                    # Global styles
│   └── index.css                  # Tailwind CSS imports
├── index.html                     # HTML template
├── package.json                   # Dependencies and scripts
├── vite.config.ts                 # Vite configuration
├── tailwind.config.js             # Tailwind CSS configuration
├── tsconfig.json                  # TypeScript configuration
├── tsconfig.app.json              # App-specific TypeScript config
├── tsconfig.node.json             # Node-specific TypeScript config
└── eslint.config.js               # ESLint configuration
```

### Component Relationships

```mermaid
graph TD
    A[App.tsx] --> B[ErrorBoundary]
    A --> C[ToastProvider]
    A --> D[Router]
    
    D --> E[MainLayout]
    E --> F[Sidebar]
    E --> G[Routes]
    
    G --> H[DashboardPage]
    G --> I[PortfolioAnalysisPage]
    G --> J[PortfolioUploadPage]
    G --> K[AdministrationPage]
    
    H --> L[PortfolioUpload]
    H --> M[PortfolioTable]
    
    I --> N[usePortfolioAnalysis]
    I --> O[PortfolioChart]
    I --> P[PortfolioMetrics]
    I --> Q[DataAvailabilityWarnings]
    
    N --> R[apiService]
    O --> S[Recharts]
    P --> T[ColorCoding]
    
    R --> U[Axios]
    U --> V[Backend API]
```

---

## 5. Core Components

### Application Structure

#### App Component (`src/App.tsx`)
- **Purpose**: Main application wrapper with routing and error handling
- **Features**:
  - Error boundary for graceful error handling
  - Toast notification provider
  - React Router setup
  - Main layout management
- **Dependencies**: ErrorBoundary, ToastProvider, Router

#### MainLayout Component (`src/App.tsx`)
- **Purpose**: Main application layout with sidebar and content area
- **Features**:
  - Responsive sidebar navigation
  - Portfolio state management
  - Route-based page rendering
  - Dynamic page titles
- **Dependencies**: Sidebar, Routes, apiService

### Page Components

#### DashboardPage (`src/pages/DashboardPage.tsx`)
- **Purpose**: Main dashboard with portfolio upload and management
- **Features**:
  - File upload with drag-and-drop
  - Portfolio table display
  - Quick stats overview
  - Getting started guide
- **Key Props**: `portfolio`, `setPortfolio`
- **Dependencies**: PortfolioUpload, PortfolioTable, apiService

#### PortfolioAnalysisPage (`src/pages/PortfolioAnalysisPage.tsx`)
- **Purpose**: Portfolio analysis and metrics display
- **Features**:
  - Date range selection
  - Analysis execution
  - Metrics visualization
  - Data availability warnings
- **Key Hooks**: `usePortfolioAnalysis`
- **Dependencies**: PortfolioChart, PortfolioMetrics, DataAvailabilityWarnings

#### PortfolioUploadPage (`src/pages/PortfolioUploadPage.tsx`)
- **Purpose**: Dedicated portfolio upload and management page
- **Features**:
  - File upload interface
  - Portfolio table with actions
  - Error and success handling
  - Portfolio refresh functionality
- **Dependencies**: PortfolioUpload, PortfolioTable, apiService

#### AdministrationPage (`src/pages/AdministrationPage.tsx`)
- **Purpose**: System administration interface
- **Features**:
  - Warehouse management
  - Log management
  - System statistics
  - Administrative operations
- **Dependencies**: apiService, ToastContext

### Portfolio Components

#### PortfolioTable (`src/components/portfolio/PortfolioTable.tsx`)
- **Purpose**: Display portfolio data in tabular format
- **Features**:
  - Responsive table design
  - Export to CSV functionality
  - Clear portfolio action
  - Refresh functionality
- **Key Props**: `portfolio`, `onClearPortfolio`, `onRefreshPortfolio`
- **Dependencies**: Lucide React icons

#### PortfolioUpload (`src/components/portfolio/PortfolioUpload.tsx`)
- **Purpose**: File upload with drag-and-drop functionality
- **Features**:
  - Drag-and-drop file handling
  - CSV file validation
  - Upload progress indicators
  - Error handling
- **Key Props**: `onUploadSuccess`, `onUploadError`
- **Dependencies**: react-dropzone, apiService

#### PortfolioChart (`src/components/portfolio/PortfolioChart.tsx`)
- **Purpose**: Performance comparison charts
- **Features**:
  - Portfolio vs benchmark comparison
  - Interactive tooltips
  - Reference lines
  - Performance optimization with useMemo
- **Key Props**: `timeSeriesData`, `metrics`
- **Dependencies**: Recharts, useMemo optimization

#### PortfolioMetrics (`src/components/portfolio/PortfolioMetrics.tsx`)
- **Purpose**: Display portfolio-level financial metrics
- **Features**:
  - Color-coded metrics based on performance
  - Compact and detailed views
  - Metric legend
  - Responsive design
- **Key Props**: `metrics`, `timeSeriesData`
- **Dependencies**: Color coding system

#### DataAvailabilityWarnings (`src/components/portfolio/DataAvailabilityWarnings.tsx`)
- **Purpose**: Display data availability issues
- **Features**:
  - Collapsible warning interface
  - Detailed data availability information
  - Missing ticker warnings
  - Start date validation warnings
- **Key Props**: `warnings`, `isExpanded`, `onToggle`
- **Dependencies**: Lucide React icons

### Utility Components

#### ErrorBoundary (`src/components/ErrorBoundary.tsx`)
- **Purpose**: React error boundary for graceful error handling
- **Features**:
  - Error catching and display
  - Error recovery options
  - Development mode error details
  - Logging integration
- **Dependencies**: Logger service

#### Logo (`src/components/Logo.tsx`)
- **Purpose**: Application logo component
- **Features**:
  - Responsive logo display
  - Consistent branding
- **Dependencies**: None

---

## 6. State Management

### React Hooks

#### usePortfolioAnalysis (`src/hooks/usePortfolioAnalysis.ts`)
- **Purpose**: Portfolio analysis state management
- **State**:
  - `analysisResults`: Analysis data and metrics
  - `isLoading`: Loading state for analysis
  - `error`: Error state and messages
  - `selectedDateRange`: Selected analysis date range
- **Methods**:
  - `runAnalysis()`: Execute portfolio analysis
  - `clearAnalysis()`: Clear analysis results
  - `setSelectedDateRange()`: Update date range
- **Dependencies**: apiService, logger, useToast

### Context Providers

#### ToastProvider (`src/contexts/ToastContext.tsx`)
- **Purpose**: Global toast notification management
- **Features**:
  - Toast state management
  - Success, error, warning, info toasts
  - Auto-dismiss functionality
  - Queue management
- **Methods**:
  - `showToast()`: Display toast notification
  - `hideToast()`: Hide specific toast
  - `clearToasts()`: Clear all toasts

### Local State Management

#### Component State
- **useState**: Local component state
- **useEffect**: Side effects and lifecycle management
- **useCallback**: Memoized functions for performance
- **useMemo**: Memoized values for expensive calculations

#### State Flow
```
User Action → Component State → Hook State → API Call → Backend
     ↓              ↓              ↓           ↓
UI Update ← State Update ← Response ← HTTP Response
```

---

## 7. API Integration

### API Service (`src/services/api.ts`)

#### Configuration
- **Base URL**: `http://localhost:8000` (configurable via env)
- **Timeout**: 5 minutes for large portfolio analysis
- **Headers**: JSON content type
- **Interceptors**: Request/response logging

#### Methods

| Method | Purpose | Request | Response |
|--------|---------|---------|----------|
| `uploadPortfolio(file)` | Upload CSV file | FormData | `PortfolioUploadResponse` |
| `getPortfolio()` | Get current portfolio | None | `Portfolio` |
| `clearPortfolio()` | Clear portfolio | None | `ApiResponse` |
| `analyzePortfolio(dateRange)` | Analyze portfolio | Query params | `PortfolioAnalysis` |
| `analyzeTickers(tickers)` | Analyze tickers | JSON body | `TickerAnalysis[]` |
| `healthCheck()` | Health check | None | `{status: string}` |

#### Error Handling
- **Axios interceptors** for request/response logging
- **Error transformation** to consistent format
- **Timeout handling** for long-running operations
- **Retry logic** for failed requests

### Type Definitions

#### Portfolio Types (`src/types/portfolio.ts`)
```typescript
interface Portfolio {
  positions: Position[];
  totalPositions: number;
  tickers: string[];
}

interface Position {
  ticker: string;
  position: number;
}

interface PortfolioAnalysis {
  success: boolean;
  message: string;
  data: PortfolioMetrics;
  warnings: DataWarnings;
  timeSeriesData: TimeSeriesData;
}
```

#### API Types (`src/types/api.ts`)
```typescript
interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}
```

---

## 8. Routing & Navigation

### React Router Setup

#### Routes Configuration
```typescript
<Routes>
  <Route path="/" element={<DashboardPage />} />
  <Route path="/portfolio/analysis" element={<PortfolioAnalysisPage />} />
  <Route path="/administration" element={<AdministrationPage />} />
</Routes>
```

#### Navigation Structure
- **Dashboard** (`/`): Portfolio upload and management
- **Portfolio Analysis** (`/portfolio/analysis`): Analysis and metrics
- **Administration** (`/administration`): System administration

#### Sidebar Navigation
- **Portfolio Management**: Upload and manage portfolios
- **Analysis Dashboard**: View portfolio analysis
- **Administration**: System administration tools
- **Settings**: Application settings

### Route Guards
- **Portfolio Analysis**: Redirects to dashboard if no portfolio loaded
- **Administration**: Accessible to all users (no authentication)
- **Dynamic Titles**: Page titles update based on current route

---

## 9. Styling & Design System

### Tailwind CSS Configuration

#### Color Palette
```css
primary: {
  50: '#eff6ff',   /* Lightest blue - backgrounds */
  100: '#dbeafe',  /* Light blue - subtle highlights */
  200: '#bfdbfe',  /* Soft blue - borders, dividers */
  300: '#93c5fd',  /* Medium light blue - hover states */
  400: '#60a5fa',  /* Medium blue - secondary actions */
  500: '#3b82f6',  /* Base blue - primary actions */
  600: '#2563eb',  /* Dark blue - active states */
  700: '#1d4ed8',  /* Darker blue - pressed states */
  800: '#1e40af',  /* Very dark blue - text on light */
  900: '#1e3a8a',  /* Darkest blue - high contrast text */
}
```

#### Typography
- **Font Family**: Inter, system-ui, sans-serif
- **Headings**: 2xl, 3xl, 4xl with font-bold
- **Body Text**: base, sm, xs with font-normal
- **Weights**: light, normal, medium, semibold, bold

#### Component Classes
```css
/* Buttons */
.btn-primary { @apply inline-flex items-center px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700; }
.btn-secondary { @apply inline-flex items-center px-4 py-2 bg-white text-gray-700 font-medium rounded-lg border border-gray-300 hover:bg-gray-50; }
.btn-danger { @apply inline-flex items-center px-4 py-2 bg-error-600 text-white font-medium rounded-lg hover:bg-error-700; }

/* Cards */
.card { @apply bg-white rounded-lg border border-gray-200 shadow-sm; }
.metric-card { @apply bg-white p-6 rounded-lg border border-gray-200 shadow-sm; }

/* Tables */
.table { @apply min-w-full divide-y divide-gray-200; }
.table th { @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider; }
.table td { @apply px-6 py-4 whitespace-nowrap text-sm; }
```

### Financial Metrics Color Coding

#### Portfolio Metrics
- **Excellent**: Green (`text-success-600`, `bg-success-50`)
- **Normal**: Yellow (`text-warning-600`, `bg-warning-50`)
- **Poor**: Red (`text-error-600`, `bg-error-50`)

#### Thresholds
- **Total Return**: Red <10%, Yellow 10-30%, Green >30%
- **Annualized Return**: Red <5%, Yellow 5-15%, Green >15%
- **Sharpe Ratio**: Red <0.5, Yellow 0.5-1.5, Green >1.5
- **Max Drawdown**: Red >-30%, Yellow -30% to -15%, Green >-15%

### Responsive Design

#### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

#### Responsive Patterns
```css
/* Grid layouts */
.grid-portfolio { @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4; }
.grid-metrics { @apply grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4; }

/* Navigation */
.nav-mobile { @apply block lg:hidden; }
.nav-desktop { @apply hidden lg:block; }

/* Tables */
.table-responsive { @apply overflow-x-auto; }
```

---

## 10. Error Handling

### Error Boundary System

#### ErrorBoundary Component
- **Purpose**: Catch JavaScript errors in component tree
- **Features**:
  - Error display with recovery options
  - Development mode error details
  - Error logging integration
  - Graceful fallback UI
- **Error Recovery**:
  - Retry button for failed operations
  - Navigation to safe pages
  - Error state reset

#### Error Types
- **Component Errors**: JavaScript errors in React components
- **API Errors**: Network and server errors
- **Validation Errors**: Input validation failures
- **File Upload Errors**: CSV parsing and upload errors

### Error Handling Patterns

#### API Error Handling
```typescript
try {
  const response = await apiService.analyzePortfolio(dateRange);
  setAnalysisResults(response.data);
} catch (error) {
  const apiError = error as ApiError;
  setError(apiError.message || 'Analysis failed');
  logger.error('Portfolio analysis failed', error);
}
```

#### Component Error Handling
```typescript
const [error, setError] = useState<string | null>(null);
const [isLoading, setIsLoading] = useState(false);

const handleError = (error: Error) => {
  setError(error.message);
  setIsLoading(false);
  logger.error('Component error', error);
};
```

### User Feedback

#### Toast Notifications
- **Success**: Green toast for successful operations
- **Error**: Red toast for errors with details
- **Warning**: Yellow toast for warnings
- **Info**: Blue toast for informational messages

#### Error Messages
- **User-friendly**: Clear, actionable error messages
- **Context-aware**: Specific to the operation that failed
- **Recovery suggestions**: Guidance on how to fix issues

---

## 11. Performance Optimizations

### React Optimizations

#### useMemo for Expensive Calculations
```typescript
const chartData = useMemo(() => {
  return processTimeSeriesData(timeSeriesData);
}, [timeSeriesData]);
```

#### useCallback for Event Handlers
```typescript
const handleAnalysis = useCallback(() => {
  runAnalysis(selectedDateRange);
}, [runAnalysis, selectedDateRange]);
```

#### Component Memoization
```typescript
const PortfolioChart = React.memo(({ timeSeriesData, metrics }) => {
  // Component implementation
});
```

### Chart Performance

#### Recharts Optimization
- **useMemo** for data processing (60%+ performance improvement)
- **Reference lines** for better data interpretation
- **Custom tooltips** with percentage change display
- **Responsive design** with proper scaling

#### Data Processing
- **Lazy loading** for large datasets
- **Data normalization** for consistent rendering
- **Memory cleanup** for chart unmounting

### Bundle Optimization

#### Vite Configuration
- **Tree shaking** for unused code elimination
- **Code splitting** for route-based chunks
- **Asset optimization** for images and fonts
- **CSS purging** for unused styles

#### Import Optimization
```typescript
// Lazy loading for heavy components
const AdministrationPage = lazy(() => import('./pages/AdministrationPage'));

// Tree-shakeable imports
import { Upload, BarChart3 } from 'lucide-react';
```

---

## 12. Logging & Monitoring

### Frontend Logging System

#### Logger Service (`src/utils/logger.ts`)
- **Log Levels**: DEBUG, INFO, WARN, ERROR, CRITICAL
- **Session Tracking**: UUID-based session correlation
- **Backend Integration**: Logs sent to backend via `/api/logs`
- **Performance Monitoring**: Operation timing and metrics

#### Logging Patterns
```typescript
// User action logging
logger.logUserAction('file_uploaded', { 
  fileName: file.name, 
  fileSize: file.size 
});

// API call logging
logger.logApiCall('POST', '/portfolio/upload', 250, true, {
  requestId: 'abc123'
});

// Error logging
logger.error('Portfolio analysis failed', error, {
  portfolioSize: portfolio.tickers.length
});
```

### Performance Monitoring

#### Metrics Tracked
- **User Actions**: File uploads, analysis runs, navigation
- **API Calls**: Request/response times, success rates
- **Component Performance**: Render times, re-renders
- **Error Rates**: Component errors, API failures

#### Monitoring Integration
- **Backend Correlation**: Logs sent to backend for analysis
- **Session Management**: Portfolio session tracking
- **Performance Metrics**: Real-time performance data

---

## 13. Testing

### Test Structure (Planned)

```
tests/
├── unit/                    # Unit tests
│   ├── components/          # Component tests
│   ├── hooks/              # Hook tests
│   └── utils/              # Utility tests
├── integration/            # Integration tests
│   ├── api/                # API integration tests
│   └── pages/              # Page integration tests
└── e2e/                    # End-to-end tests
    ├── portfolio/          # Portfolio workflows
    └── administration/     # Admin workflows
```

### Testing Tools

#### Unit Testing
- **Jest**: JavaScript testing framework
- **React Testing Library**: Component testing utilities
- **MSW**: API mocking for tests

#### Integration Testing
- **Cypress**: End-to-end testing
- **Playwright**: Cross-browser testing
- **Storybook**: Component development and testing

### Test Categories

#### Component Tests
- **Rendering**: Component renders correctly
- **Props**: Props are handled properly
- **Events**: User interactions work
- **State**: State updates correctly

#### Hook Tests
- **State Management**: Hook state updates
- **Side Effects**: useEffect behavior
- **API Integration**: API calls and responses
- **Error Handling**: Error states and recovery

#### Integration Tests
- **API Integration**: Backend communication
- **User Workflows**: Complete user journeys
- **Error Scenarios**: Error handling and recovery
- **Performance**: Load times and responsiveness

---

## 14. Build & Deployment

### Build Configuration

#### Vite Configuration (`vite.config.ts`)
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000
  }
});
```

#### TypeScript Configuration
- **tsconfig.json**: Main TypeScript configuration
- **tsconfig.app.json**: Application-specific config
- **tsconfig.node.json**: Node.js-specific config

### Build Process

#### Development
```bash
npm run dev          # Start development server
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

#### Production
```bash
npm run build        # Build for production
npm run preview      # Preview production build
```

#### Build Output
- **Static Assets**: HTML, CSS, JS bundles
- **Asset Optimization**: Minified and compressed
- **Source Maps**: For debugging production builds
- **Environment Variables**: Injected at build time

### Environment Configuration

#### Environment Variables
- **VITE_API_BASE_URL**: Backend API URL
- **VITE_APP_VERSION**: Application version
- **VITE_DEBUG**: Debug mode flag

#### Development vs Production
- **Development**: Hot reload, source maps, debug info
- **Production**: Minified, optimized, compressed
- **Environment-specific**: Different API URLs and configs

---

## 15. Development Guidelines

### Code Organization

#### Component Structure
```typescript
// Component file structure
interface ComponentProps {
  // Props interface
}

const Component: React.FC<ComponentProps> = ({ prop1, prop2 }) => {
  // Hooks
  const [state, setState] = useState();
  
  // Effects
  useEffect(() => {
    // Side effects
  }, []);
  
  // Handlers
  const handleAction = useCallback(() => {
    // Action logic
  }, []);
  
  // Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
};

export default Component;
```

#### File Naming Conventions
- **Components**: PascalCase (e.g., `PortfolioTable.tsx`)
- **Hooks**: camelCase with `use` prefix (e.g., `usePortfolioAnalysis.ts`)
- **Utils**: camelCase (e.g., `timeoutCalculator.ts`)
- **Types**: camelCase (e.g., `portfolio.ts`)

### TypeScript Guidelines

#### Type Safety
- **Strict Mode**: Enable strict TypeScript settings
- **Interface Definitions**: Define interfaces for all data structures
- **Generic Types**: Use generics for reusable components
- **Type Guards**: Implement type guards for runtime type checking

#### Best Practices
```typescript
// Interface definitions
interface PortfolioProps {
  portfolio: Portfolio;
  onUpdate: (portfolio: Portfolio) => void;
}

// Generic components
interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
}

// Type guards
const isApiError = (error: unknown): error is ApiError => {
  return error !== null && typeof error === 'object' && 'message' in error;
};
```

### Component Guidelines

#### Component Design
- **Single Responsibility**: One component, one purpose
- **Props Interface**: Define clear prop interfaces
- **Default Props**: Use default props for optional values
- **Memoization**: Use React.memo for expensive components

#### State Management
- **Local State**: Use useState for component-specific state
- **Global State**: Use context for shared state
- **Derived State**: Use useMemo for computed values
- **Side Effects**: Use useEffect for side effects

### Performance Guidelines

#### Optimization Strategies
- **Memoization**: Use useMemo and useCallback appropriately
- **Lazy Loading**: Implement lazy loading for heavy components
- **Bundle Splitting**: Split code by routes and features
- **Asset Optimization**: Optimize images and fonts

#### Memory Management
- **Cleanup**: Clean up subscriptions and timers
- **Unmounting**: Handle component unmounting properly
- **Memory Leaks**: Avoid memory leaks in effects
- **Resource Management**: Manage resources efficiently

### Error Handling Guidelines

#### Error Boundaries
- **Component Level**: Wrap components in error boundaries
- **Page Level**: Implement page-level error boundaries
- **Global Level**: Use global error boundary for app-level errors

#### Error Recovery
- **User Feedback**: Provide clear error messages
- **Recovery Actions**: Offer recovery options
- **Logging**: Log errors for debugging
- **Graceful Degradation**: Fallback to safe states

---

## Conclusion

This frontend documentation provides a comprehensive overview of the React-based portfolio analysis application. The system features a modern, responsive design with comprehensive financial data visualization, robust error handling, and performance optimizations.

Key strengths:
- **Modern Architecture**: React 19 with TypeScript and modern tooling
- **Performance**: Optimized with memoization and lazy loading
- **User Experience**: Intuitive interface with comprehensive feedback
- **Maintainability**: Clean code organization and TypeScript safety
- **Scalability**: Modular component architecture for easy extension

For questions or updates to this documentation, please refer to the project's technical documentation or contact the development team.

---

*Last updated: January 2025*
*Version: 1.0.0*
