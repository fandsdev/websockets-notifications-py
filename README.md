### websockets-notifications Demo

This project requires Python 3.12+.
Dependencies are managed by [uv](https://github.com/astral-sh/uv) and should be installed.
The list of requirements is stored in `pyproject.toml`.

### Some Facts About Environment Variables:
1. When running in a container, do not forget to set `WEBSOCKETS_HOST` in the environment variables. In most cases, it should be `0.0.0.0`.
2. The app requires a JWT public key for authentication. It can be set using one of two options (if both are set, the app will not start):
    1. Environment variable `JWT_PUBLIC_KEY`. Ensure it has no newlines. Check `env.example` for the correct format.
    2. A file named `jwt_public_key.pem` inside the `src` directory.

### Develop on a Local Machine
Install and activate a virtual environment:
```bash
uv venv
source venv/bin/activate
```

Set environment variables
```bash
cp env.example ./src/.env  # default environment variables
```

Install requirements:
```bash
make  # compile and install deps
```

Run message broker:
```bash
docker compose up -d
```

Run server:
```bash
cd python src/entrypoint.py
```

Connect to the server in cli:
```bash
python -m websockets ws://localhost:{% port %}/{% websockets_path % }
```

Format code with ruff
```bash
make fmt
```

Run linters
```bash
make lint
```

Run tests
```bash
make test
```

## Build docker image
If you need to set python version manually
```bash
docker build --build-arg "PYTHON_VERSION=3.11.6" --tag websocket-notifications .
```

Preferred way is to use `.python-version` file
```bash
docker build --build-arg "PYTHON_VERSION=$(cat .python-version)" --tag websocket-notifications .
```
