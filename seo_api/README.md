# SEO Content Generator Platform

A comprehensive platform for SEO specialists and content writers to generate, optimize, and manage content for multiple clients with personalized style adaptation.

## Overview

This system consists of two main components:

1. **SEO Optimization Engine** - Powerful AI Agents for content generation and SEO optimization pipeline using puissant and dynamic LLMs
2. **Content Management API** - A REST API for user management, client management, and content storage build using FastAPI

The platform allows SEO specialists to:
- Manage multiple clients and their preferences
- Generate SEO-optimized content tailored to client needs
- Analyze and adapt writing styles based on reference materials
- Store and organize various content types for each client

## System Architecture

```
├── Spinutech 
│   └── seo_api/                     # Content management REST API
│       ├── app/                     # API application
│       │   ├── api/                 # API endpoints
│       │   ├── models/              # Data models
│       │   ├── schemas/             # Request/response schemas
│       │   ├── services/            # Business logic
│       │   └── utils/               # Utility functions
│       ├── run.py                   # API server entry point
│       └── requirements.txt         # API dependencies
│
└── data/                            # Data storage
    └── users/                       # User-specific data
        └── {user_email}/            # Individual user data
            ├── profile.json         # User profile
            ├── style_profile.json   # Writing style analysis
            ├── files/               # User reference files
            └── clients/             # Client data
                └── {client_id}/     # Individual client data
                    ├── metadata.json # Client details
                    ├── preferences.json # Client preferences
                    ├── files/       # Client reference files
                    └── content/     # Generated content
```

## Features

### User Management
- User registration and authentication with JWT
- Role-based access (SEO Specialist, Content Writer, Account Manager)
- User profile management
- Writing style analysis and adaptation

### Client Management
- Create and manage multiple clients
- Store client preferences and industry information
- Organize content by client and content type
- Reference content storage for style analysis

### Content Generation
- SEO-optimized content generation
- Support for multiple content types (articles, product descriptions, landing pages)
- Customizable tone and style
- Keyword optimization
- Competitive analysis integration

### File Management
- Upload reference documents (PDF, DOCX, TXT)
- Analyze writing styles from uploaded documents
- Store and retrieve client brand guidelines
- Manage content assets

## Getting Started

### Prerequisites
- Python 3.10+
- Virtual environment tool (venv, conda, etc.)
- OpenAI API key or equivalent LLM API access

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ris3abh/Spinutech.git
cd Spinutech
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create configuration files:
```bash
# Create .env file in seo_api directory
cp seo_api/.env.example seo_api/.env
# Edit .env file with your configuration

# Create .env file in SEOoptimization directory
cp SEOoptimization/.env.example SEOoptimization/.env
# Edit .env file with your configuration
```

### Running the API Server

```bash
cd seo_api
python run.py
```

The API will be available at http://localhost:8000 with interactive documentation at http://localhost:8000/docs.

### Running the SEO Optimization Tool

The SEO optimization engine can be used via the API or directly through the command line:

```bash
cd SEOoptimization
python SEOoptimization/run.py --topic "Your Topic" --tone "professional" --length "1200 words" --keywords "keyword1, keyword2, keyword3" --debug --save
```

## API Documentation

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register a new user |
| `/api/v1/auth/login` | POST | Login and get access token |
| `/api/v1/auth/token` | POST | OAuth2 compatible token endpoint |

### User Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/users/me` | GET | Get current user profile |
| `/api/v1/users/me` | PUT | Update user profile |
| `/api/v1/users/me/style` | GET | Get user writing style profile |
| `/api/v1/users/me/clients` | GET | List user clients |

### Client Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/clients` | POST | Create a new client |
| `/api/v1/clients` | GET | List all clients |
| `/api/v1/clients/{client_id}` | GET | Get client details |
| `/api/v1/clients/{client_id}` | PUT | Update client information |
| `/api/v1/clients/{client_id}/preferences` | GET | Get client preferences |
| `/api/v1/clients/{client_id}/preferences` | POST | Create client preferences |
| `/api/v1/clients/{client_id}/preferences` | PUT | Update client preferences |

### File Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/files/user/style-reference` | POST | Upload user style reference |
| `/api/v1/files/user/style-reference` | GET | List user style references |
| `/api/v1/files/user/style-reference/{filename}` | GET | Download user style reference |
| `/api/v1/files/user/style-reference/{filename}` | DELETE | Delete user style reference |
| `/api/v1/files/client/{client_id}/reference-content` | POST | Upload client reference content |
| `/api/v1/files/client/{client_id}/reference-content` | GET | List client reference content |
| `/api/v1/files/client/{client_id}/reference-content/{filename}` | GET | Download client reference content |
| `/api/v1/files/client/{client_id}/reference-content/{filename}` | DELETE | Delete client reference content |

### Content Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/content/generate` | POST | Generate new content |
| `/api/v1/content/client/{client_id}` | GET | List content for a client |
| `/api/v1/content/client/{client_id}/{content_id}` | GET | Get specific content |
| `/api/v1/content/client/{client_id}/{content_id}` | PUT | Update content |
| `/api/v1/content/client/{client_id}/{content_id}` | DELETE | Delete content |

### SEO Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/seo/analyze` | POST | Analyze keywords for SEO |
| `/api/v1/seo/optimize` | POST | Optimize existing content for SEO |

## Data Models

### User

```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "company": "SEO Agency",
  "role": "content_writer",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00",
  "clients": ["client1", "client2"]
}
```

### Client

```json
{
  "client_id": "acme-corp",
  "client_name": "Acme Corporation",
  "industry": "Technology",
  "specialist_email": "user@example.com",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00",
  "content_types": ["articles", "landing_page"]
}
```

### Client Preferences

```json
{
  "tone": "professional",
  "style_notes": "Use industry-specific jargon, avoid contractions",
  "brand_guidelines": {
    "voice": "Authoritative but approachable",
    "prohibited_terms": ["cheap", "budget", "low-cost"]
  },
  "target_audience": ["IT professionals", "C-level executives"],
  "voice_characteristics": ["technical", "precise", "confident"],
  "taboo_topics": ["competitor names", "pricing criticism"],
  "competitors": ["CompetitorA", "CompetitorB"]
}
```

## Content Generation Workflow

1. **Authentication** - User authenticates with the API
2. **Client Selection** - User selects a client to generate content for
3. **Content Parameters** - User provides topic, tone, keywords, and other parameters
4. **SEO Analysis** - System analyzes top-ranking content for the topic
5. **Content Generation** - System generates an initial content draft
6. **Style Adaptation** - System adapts content to match client style preferences
7. **SEO Optimization** - System optimizes content for search engines
8. **Content Delivery** - Optimized content is returned to the user

## Future Enhancements

1. **Advanced Style Analysis** - Enhanced LLM-based analysis of writing styles
2. **Multi-Format Support** - Additional content types (scripts, video descriptions, etc.)
3. **Workflow Automation** - Content approval workflows and scheduling
4. **Performance Analytics** - Track content performance over time
5. **Integration with CMS** - Direct publishing to WordPress, Shopify, etc.
6. **Team Collaboration** - Multiple users working on the same client
7. **Content Versioning** - Track changes and revisions
8. **Enhanced SEO Analysis** - Integration with third-party SEO tools