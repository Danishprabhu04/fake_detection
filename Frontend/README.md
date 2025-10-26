# YouTube Fake Detection System - Frontend

A modern, responsive React frontend application for the YouTube Fake Detection System. Built with TypeScript, Vite, and Tailwind CSS, providing a professional interface for analyzing YouTube videos for authenticity using AI-powered detection.

![React](https://img.shields.io/badge/React-18.2.0-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0.0-blue)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.4.0-blue)
![Vite](https://img.shields.io/badge/Vite-5.0.0-purple)

## 🌟 Features

### 🔐 Authentication System
- **User Registration** - Sign up with name, email, and password
- **User Login** - Secure authentication with JWT tokens
- **Protected Routes** - Route protection for authenticated users
- **Token Management** - Automatic token refresh and storage

### 📹 Video Analysis
- **YouTube URL Analysis** - Paste any YouTube video URL for analysis
- **Real-time Processing** - Live analysis with progress indicators
- **Comprehensive Results** - Detailed authenticity assessment including:
  - Overall confidence score
  - Thumbnail analysis with authenticity flags
  - Comment sentiment analysis
  - Video metadata verification
- **Professional UI** - Clean, modern interface with gradient designs

### 📊 Dashboard
- **Welcome Interface** - Professional landing page
- **Feature Showcase** - AI Analysis, Comment Analysis, Metadata Check, Visual Detection
- **FAQ Section** - Expandable frequently asked questions
- **Responsive Design** - Perfect on all devices

### 📄 Reporting
- **Detailed Reports** - Generate comprehensive analysis reports
- **Download Functionality** - Export reports as text files
- **Professional Format** - Structured report with all analysis data

### 📱 Responsive Design
- **Mobile First** - Optimized for mobile devices
- **Tablet Support** - Perfect layout for tablets
- **Desktop Experience** - Full-featured desktop interface
- **Cross-browser** - Compatible with all modern browsers

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18.0.0 or higher)
- **npm** (v9.0.0 or higher)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd youtube-fake-detection-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` with your configuration:
   ```env
   REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
   REACT_APP_USE_MOCK_API=true
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   ```
   http://localhost:5173
   ```

## 📁 Project Structure

```
Frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── ui/           # Shadcn/ui components
│   │   └── ProtectedRoute.tsx
│   ├── contexts/         # React contexts
│   │   └── AuthContext.tsx
│   ├── hooks/           # Custom React hooks
│   │   └── use-toast.ts
│   ├── lib/             # Utility libraries
│   │   └── utils.ts
│   ├── pages/           # Application pages
│   │   ├── Analyze.tsx  # Video analysis page
│   │   ├── Dashboard.tsx # Main dashboard
│   │   ├── SignIn.tsx   # Login page
│   │   └── SignUp.tsx   # Registration page
│   └── services/        # API services
│       └── api.ts       # API integration layer
├── .env.example         # Environment template
├── package.json
├── tailwind.config.js   # Tailwind configuration
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## 🎨 UI Components

Built with **shadcn/ui** and **Tailwind CSS** for a modern, consistent design:

- **Cards** - Professional content containers
- **Buttons** - Multiple variants with loading states
- **Forms** - Input validation and error handling
- **Progress Bars** - Visual progress indicators
- **Badges** - Status and category indicators
- **Accordions** - Expandable content sections
- **Toasts** - User notifications and feedback

## 🔧 Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking

# Testing
npm run test         # Run tests (when configured)
```

## 🌐 API Integration

The frontend is designed to work with the YouTube Fake Detection System backend. API integration is handled through a centralized service layer.

### Backend Endpoints Supported

- **Authentication**: `/auth/register`, `/auth/login`, `/auth/refresh`
- **Video Analysis**: `/videos/analyze`, `/videos/{id}`, `/videos/trending`
- **Reports**: `/reports/create`, `/reports/summary`, `/reports/{id}`
- **Analytics**: `/analytics/trends`, `/analytics/regions`, `/analytics/categories`

### Integration Guide

See [`API_INTEGRATION_GUIDE.md`](./API_INTEGRATION_GUIDE.md) for detailed backend integration instructions.

## 🔒 Environment Variables

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1

# Environment
REACT_APP_ENV=development

# Mock Mode (set to false when connecting to real API)
REACT_APP_USE_MOCK_API=true
```

## 📱 Responsive Breakpoints

```css
/* Tailwind CSS breakpoints used */
sm: 640px    /* Small devices (landscape phones) */
md: 768px    /* Medium devices (tablets) */
lg: 1024px   /* Large devices (desktops) */
xl: 1280px   /* Extra large devices */
```

## 🎯 Browser Support

- **Chrome** (v90+)
- **Firefox** (v88+)
- **Safari** (v14+)
- **Edge** (v90+)

## 🛠️ Technology Stack

### Core Technologies
- **React 18.2.0** - UI library with hooks and context
- **TypeScript 5.0.0** - Type safety and better development experience
- **Vite 5.0.0** - Fast build tool and development server

### Styling & UI
- **Tailwind CSS 3.4.0** - Utility-first CSS framework
- **shadcn/ui** - High-quality React components
- **Framer Motion** - Smooth animations and transitions
- **Lucide React** - Beautiful icons

### Routing & State
- **React Router DOM** - Client-side routing
- **Context API** - Global state management for authentication

### Development Tools
- **ESLint** - Code linting and formatting
- **PostCSS** - CSS processing
- **Autoprefixer** - CSS vendor prefixing

## 🚦 Development Guidelines

### Code Style
- **TypeScript** for type safety
- **Functional components** with hooks
- **Custom hooks** for reusable logic
- **Context API** for global state
- **Utility-first** CSS with Tailwind

### File Naming
- **Components**: PascalCase (e.g., `SignIn.tsx`)
- **Hooks**: camelCase starting with 'use' (e.g., `useToast.ts`)
- **Utilities**: camelCase (e.g., `utils.ts`)
- **Constants**: UPPER_SNAKE_CASE

### Component Structure
```tsx
// Import order: React -> External libs -> Internal components -> Types
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';

interface ComponentProps {
  // Props interface
}

export const Component = ({ prop }: ComponentProps) => {
  // Component implementation
};
```

## 🧪 Testing

Testing framework setup is ready for:
- **Unit Tests** - Component testing
- **Integration Tests** - API integration testing
- **E2E Tests** - End-to-end user flow testing

## 📦 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Vercel
```bash
npm install -g vercel
vercel --prod
```

### Deploy to Netlify
```bash
npm run build
# Upload dist/ folder to Netlify
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Built with ❤️ using React, TypeScript, and Tailwind CSS**