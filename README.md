# Sentinel

> "The best kind of incident is the one that is never raised" - Saahil Pandya

**Sentinel** is an intelligent, AI-powered IT Service Management (ITSM) platform designed to modernize incident response and operations. Built for scalability and speed, Sentinel leverages advanced AI to predict, prevent, and resolve incidents before they impact your business.

## Key Features

-   **AI-Driven Insights**: Powered by a dedicated "Brain" module and Vector Search (pgvector) to provide intelligent context and automated resolution suggestions.
-   **Multi-Tenancy Architecture**: Built from the ground up to support multiple organizations and workspaces securely.
-   **Real-Time Collaboration**: Seamless incident management workflows designed for high-velocity teams.
-   **Modern & Responsive UI**: A beautiful, premium interface built with **Next.js 16**, **Tailwind CSS v4**, and **Framer Motion**.
-   **Enterprise-Grade Security**: robust authentication and role-based access control.

## Tech Stack

### Backend
-   **Framework**: Python (FastAPI)
-   **Database**: PostgreSQL (with `pgvector` extension for AI capabilities)
-   **Migrations**: Alembic
-   **Containerization**: Docker & Docker Compose

### Frontend
-   **Framework**: Next.js 16 (App Router)
-   **Language**: TypeScript
-   **Styling**: Tailwind CSS v4
-   **Components**: Radix UI, Lucide Icons
-   **State/Forms**: React Hook Form, Zod
-   **Animation**: Framer Motion

## Getting Started

Follow these steps to set up the project locally.

### Prerequisites
-   **Docker** and **Docker Compose** installed on your machine.
-   **Node.js 20+** (if running frontend locally without Docker).
-   **Python 3.11+** (if running backend locally without Docker).

### Quick Start (Docker)

1.  **Clone the repository**
    ```bash
    git clone https://github.com/saahilll/sentinel.git
    cd sentinel
    ```

2.  **Start the application**
    ```bash
    docker-compose up --build
    ```
    This will start:
    -   PostgreSQL database (`sentinel-db`) on port `5432`
    -   Backend API (`sentinel-backend`) on port `8000`
    -   Adminer (Database Viewer) on port `8080`

3.  **Access the application**
    -   **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
    -   **Frontend**: (Navigate to the `frontend` directory and run `npm run dev` if not dockerized, or access via container if configured).

### Manual Setup (Development)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the UI.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
