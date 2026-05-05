# Secret Message Board (Backend Case Study)

An enterprise-grade, privacy-first messaging API built with the **FastAPI + SQLModel + Alembic** stack. This project demonstrates advanced backend patterns, including **Cryptographic Data Persistence**, **Logical TTL Enforcement**, and **API Rate Limiting**.

## 🏗️ Architectural Pillars

### 1. Cryptographic Persistence (At-Rest)
To ensure **Zero-Knowledge** storage, this system implements **Symmetric Encryption** using AES-128 in CBC mode (via `cryptography.fernet`).
*   **Implementation:** Plaintext is intercepted at the Service Layer and encrypted into `LargeBinary` blobs before being committed to the database.
*   **Security Trade-off:** By prioritizing **Confidentiality** over **Searchability**, the system intentionally disables server-side indexing on message content to prevent data leakage.

### 2. Ephemeral Lifecycle (TTL Strategy)
The system maintains a "Clean Slate" policy through a **Time-To-Live (TTL)** mechanism.
*   **Logic:** A query-time filter dynamically excludes records exceeding a 24-hour retention window.
*   **Resource Management:** This prevents database bloat and ensures the SQLite I/O remains performant even with high traffic volume.

### 3. API Defense & Rate Limiting
To protect against **DDoS** and automated flooding, the system utilizes a **Fixed-Window Rate Limiting** middleware.
*   **Engine:** [SlowAPI](https://github.com) (based on the `limits` library).
*   **Granularity:** Tracking is performed at the **Remote IP Address** level, ensuring fair resource allocation and preventing SQLite "Database Locked" errors from flood-exhaustion.

---

## 🛠️ Technical Stack


| Component | Technology | Responsibility |
| :--- | :--- | :--- |
| **Framework** | **FastAPI** | Asynchronous I/O & OpenAPI (Swagger) Generation |
| **ORM** | **SQLModel** | Unified Data Validation (Pydantic) & ORM (SQLAlchemy) |
| **Migrations** | **Alembic** | Version-controlled DDL & Schema Evolutions |
| **Encryption** | **Fernet** | Standardized Symmetric-key cryptography |
| **Middleware** | **SlowAPI** | In-memory Rate Limiting and Defense |

---

## ⚙️ Operational Setup

### Environment Configuration
The application requires the following secrets to be injected into the runtime environment:
```bash
ENCRYPTION_KEY="<base64-encoded-fernet-key>"  # Mandatory for data integrity
DATABASE_URL="sqlite:///./secrets.db"         # Persistent storage target
```

### CI/CD Deployment (Render/Linux)
1. **Dependency Resolution:** `pip install -r requirements.txt`
2. **Schema Migration:** `alembic upgrade head`
3. **Execution:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 📈 Future Roadmap
- [ ] **Background Cleanup:** Implement `FastAPI BackgroundTasks` for physical row deletion (Hard Delete).
- [ ] **Managed Persistence:** Transition from SQLite to **PostgreSQL** for concurrent transaction support.
- [ ] **Secret Management:** Integration with **HashiCorp Vault** or **AWS KMS** for key rotation.
