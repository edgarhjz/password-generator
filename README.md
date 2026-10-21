# Password Generator

A hardened, cryptographically secure password generator web application with server-side generation, strength evaluation, and containerized deployment.

## Features

- Generate cryptographically secure, unbiased passwords using Python's `secrets` module (`secrets.choice` + `secrets.SystemRandom().shuffle()`)
- Guarantees inclusion of every selected character class (uppercase, lowercase, numbers, symbols) with exact requested length
- Customizable length (4–64 characters via UI slider; 4–128 via API)
- Real-time password strength scoring (`0/5` to `5/5`) returned in a single round-trip
- Copy to clipboard functionality
- Responsive UI with non-blocking error feedback

## Tech Stack

- **Backend**: Flask 3.1 + Gunicorn 23.0 (Python 3.11)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Containerization**: Docker / Podman Compose (non-root, read-only rootfs)
- **Reverse Proxy**: Nginx (`nginxinc/nginx-unprivileged:alpine`)

## Requirements

- Python 3.11+
- Docker or Podman (`docker compose` / `podman-compose`)

## Quick Start

### Local Development & Containers

```bash
# Start all services
docker compose up --build
# or with Podman:
podman-compose up --build

# Run individually
cd backend && python app.py                                                  # Backend on port 5001
cd frontend && docker build -t frontend . && docker run -p 3000:8080 frontend # Frontend on port 3000
```

### Build & Deploy

```bash
# Build images
docker compose build

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f
```

### Running Tests

```bash
cd backend
pytest -v
# or using standard library unittest:
python3 -m unittest -v
```

## API Endpoints

### Generate Password (`POST /api/generate`)

Generates a password and returns both the password and its strength validation in a single response:

```bash
curl -X POST http://localhost:5001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"length": 16, "use_uppercase": true, "use_lowercase": true, "use_numbers": true, "use_symbols": true}'
```

### Validate Password (`POST /api/validate`)

```bash
curl -X POST http://localhost:5001/api/validate \
  -H "Content-Type: application/json" \
  -d '{"password": "MyP@ssw0rd!23"}'
```

### Health Check (`GET /api/health`)

```bash
curl http://localhost:5001/api/health
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_DEBUG` | Enable debug mode (`1`/`true`/`yes`) | `0` |
| `HOST` | Backend bind address | `0.0.0.0` |
| `PORT` | Backend listen port | `5001` |
| `MIN_PASSWORD_LENGTH` | Minimum allowed password length | `4` |
| `MAX_PASSWORD_LENGTH` | Maximum allowed password length | `128` |
| `MAX_CONTENT_LENGTH` | Max HTTP request payload size (bytes) | `16384` (16 KB) |
| `PASSWORD_SYMBOLS` | Allowed symbol character set | `!@#$%^&*()_+-=[]{}|;:,.<>?` |

## Security Notes

- **Cryptographic Randomness**: Passwords use `secrets.choice` and `secrets.SystemRandom().shuffle()` to guarantee character class inclusion without positional bias.
- **DoS & Input Protection**: Request bodies are capped at 16 KB, password lengths are bounded (`4–128`), and `/api/` requests are rate-limited in Nginx (`10r/s`, burst `20`).
- **Container Hardening**: Both backend (`appuser`, UID `1001`) and frontend (`nginx-unprivileged` on port `8080`) run as non-root users with `read_only: true` root filesystems and `no-new-privileges:true`.
- **Network Isolation**: Backend port `5001` binds to `127.0.0.1` on the host and communicates with Nginx over `password-gen-network`.
- **Security Headers**: Nginx enforces `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, and `server_tokens off`.

## License

MIT
