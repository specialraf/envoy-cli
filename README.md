# envoy-cli

> A smart CLI tool for managing and syncing `.env` files across projects with encrypted remote storage support.

---

## Installation

```bash
pip install envoy-cli
```

Or with pipx for isolated installs:

```bash
pipx install envoy-cli
```

---

## Requirements

- Python 3.8+
- An S3-compatible, GCS, or Azure Blob Storage bucket

---

## Usage

```bash
# Initialize envoy in your project
envoy init

# Push your .env file to encrypted remote storage
envoy push --env .env.production

# Pull and decrypt the latest .env for your project
envoy pull --project my-app --env production

# List all stored environments
envoy list

# Sync across all configured projects
envoy sync --all
```

Envoy uses AES-256 encryption before transmitting any secrets. Credentials are stored locally in `~/.envoy/config.toml`.

---

## Configuration

```toml
# ~/.envoy/config.toml
[remote]
provider = "s3"          # s3 | gcs | azure
bucket   = "my-secrets"
region   = "us-east-1"

[auth]
encryption_key_file = "~/.envoy/key"  # path to your local AES key file
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE) © 2024 envoy-cli contributors
