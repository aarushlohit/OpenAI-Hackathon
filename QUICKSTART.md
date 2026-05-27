# Quick Start

## 1. Create `.env`

```bash
cp .env.example .env
```

Add:

- `OPENAI_API_KEY`
- `NVIDIA_NIM_API_KEY`

## 2. Boot Runtime

```bash
docker compose up --build
```

Or use the MVP launcher:

```bash
./scripts/start_hermes.sh
```

## 3. Validate Runtime

```bash
python scripts/final_runtime_validation.py --json
```

## 4. Run Investigation

```bash
python hermes.py investigate "Telegram HR asking refundable onboarding fee"
```

## 5. Start Flutter UI

```bash
cd frontend/flutter_app
flutter pub get
flutter run
```

## 6. Open API Docs

http://localhost:8000/docs

## 7. Open Neo4j Optional

http://localhost:7474

