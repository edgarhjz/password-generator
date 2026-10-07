# Password Generator

A secure password generator web application with client-side validation and server-side generation.

## Features

- Generate cryptographically secure passwords using Python's `secrets` module
- Customizable length (4-64 characters)
- Character type selection: uppercase, lowercase, numbers, symbols
- Real-time password strength validation
- Copy to clipboard functionality
- Responsive, modern UI

## Tech Stack

- **Backend**: Flask (Python 3.11)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Containerization**: Docker/Podman
- **Reverse Proxy**: Nginx

## Requirements

- Python 3.11+
- Docker or Podman
- Nginx (included in container)

## Quick Start

### Local Development

```bash
# Start all services
docker compose up

# Or run individually
cd backend && python app.py          # Backend on port 5001
cd frontend && docker build -t frontend . && docker run -p 3000:80 frontend  # Frontend on port 3000
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

## API Endpoints

### Generate Password

```bash
curl -X POST http://localhost:5001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"length": 16, "use_uppercase": true, "use_lowercase": true, "use_numbers": true, "use_symbols": false}'
```

### Validate Password

```bash
curl -X POST http://localhost:5001/api/validate \
  -H "Content-Type: application/json" \
  -d '{"password": "MyP@ssw0rd!"}'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Debug mode | `1` |

## Security Notes

- Passwords are generated using Python's `secrets` module (cryptographically secure)
- No sensitive data is stored or transmitted
- Nginx proxies API requests to backend with proper header forwarding
- Frontend is self-contained; no external dependencies

## License

MIT
