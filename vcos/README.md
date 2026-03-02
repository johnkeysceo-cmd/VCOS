# VCOS - Viral Content Operating System

A production-grade distribution intelligence system for creating and optimizing viral content.

## Overview

VCOS is a modular, scalable microservices architecture designed to maximize content distribution performance through:

- **Hook Intelligence**: CTR optimization through curiosity gap modeling
- **Retention Engineering**: Watch time maximization via pacing and dopamine rhythm control
- **Variant Scaling**: Automatic generation of 10-20 variants per video
- **Data Feedback Compounding**: Continuous learning from performance data
- **ScreenArc Integration**: Full integration with ScreenArc for professional video processing

## Architecture

```
vcos/
├── gateway/              # API gateway and routing
├── services/            # Core microservices
│   ├── topic_engine/           # Idea generation & clustering
│   ├── hook_engine/            # Hook generation & scoring
│   ├── recording_service/      # Screen capture + ScreenArc integration
│   ├── retention_optimizer/    # Watch time optimization
│   ├── variant_generator/      # Multi-variant generation
│   ├── title_thumbnail_engine/ # Platform-specific optimization
│   ├── export_service/        # Platform export & upload
│   ├── analytics_ingestion/    # Metrics collection
│   ├── feedback_trainer/      # Reinforcement learning
│   └── prioritization_engine/  # Content planning
├── shared/              # Shared utilities
├── data/                # Data storage
├── orchestration/       # Pipeline management
├── infra/              # Infrastructure config
├── models/             # ML models
├── experiments/        # A/B testing
└── monitoring/         # Observability
```

## Key Features

### 1. Hook Generation Module
- Template library with emotional angle categorization
- Specificity enhancement (turns "few days" → "72 hours")
- Curiosity gap scoring
- Historical performance weighting

### 2. Retention Optimizer Pipeline
- Silence detection and removal (>150ms pauses)
- Sentence momentum analysis
- Idea boundary detection with zoom injection
- Outcome preview injection (0.5-1.5s at start)
- Dopamine rhythm modulation (micro stimulus every 2-4s)

### 3. Multi-Variant Auto Exporter
- Hook variants
- Pacing variants (1.0x - 1.12x speed)
- Zoom pattern variants (via ScreenArc)
- Subtitle style variants
- Generates 10-20 files per base video

### 4. ScreenArc Integration
- Full integration with generation_content/screenarc
- Python wrappers for ScreenArc CLI
- Automatic zoom effect application
- Professional video processing with presets
- Batch processing support

### 5. Analytics Ingestion
- Platform-specific clients (TikTok, Instagram, YouTube)
- Metrics normalization
- Retention curve storage
- Velocity tracking
- Time-series analytics database

### 6. Feedback Training Loop
- Hook template weight updates
- Emotional angle performance ranking
- Cluster strength modeling
- Pacing optimization
- Reinforcement learning loop

### 7. Topic Prioritization
- Cluster scoring
- Momentum prediction
- Topic recommendations
- Content calendar generation

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Node.js is installed (for ScreenArc CLI):
```bash
node --version
```

3. Install ScreenArc dependencies (if needed):
```bash
cd generation_content/screenarc
npm install
```

4. Ensure FFmpeg is available (or use bundled binaries from `generation_content/screenarc/binaries/`)

5. Initialize databases:
```python
from services.topic_engine.topic_db import init_db
from services.hook_engine.hook_db import init_db
from services.analytics_ingestion.analytics_db import init_db

# Databases auto-initialize on import
```

## Usage

### Start the Gateway API

```bash
cd vcos
python gateway/api_server.py
```

The API will be available at `http://localhost:8000`

### Create a Batch

```bash
curl -X POST http://localhost:8000/api/v1/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: internal-secret-change-in-production" \
  -d '{
    "topic": "Rebuilt Screen Studio in 24h",
    "num_variants": 20,
    "platforms": ["tiktok", "instagram", "youtube"]
  }'
```

### Check Batch Status

```bash
curl http://localhost:8000/api/v1/batch/{job_id} \
  -H "X-API-Key: internal-secret-change-in-production"
```

### Generate Hooks

```bash
curl -X POST http://localhost:8000/api/v1/hook/generate \
  -H "X-API-Key: internal-secret-change-in-production" \
  -d '{"topic": "Building a better screen recorder"}'
```

### Get Topic Recommendations

```bash
curl http://localhost:8000/api/v1/topic/suggest \
  -H "X-API-Key: internal-secret-change-in-production"
```

## ScreenArc Integration

The Recording Service fully integrates with ScreenArc:

```python
from services.recording_service import process_video_with_screenarc

result = process_video_with_screenarc(
    input_video="input.mp4",
    output_video="output.mp4",
    preset="cinematic",  # or "minimal", "youtube", "short", "instagram", "clean", "dark"
    metadata_path="metadata.json"  # Optional ScreenArc metadata
)
```

### Available Presets

- `cinematic`: Default cinematic look with shadows
- `minimal`: Minimal styling with subtle effects
- `youtube`: Optimized for YouTube (gradient bg)
- `short`: TikTok/Shorts vertical format (9:16)
- `instagram`: Square format for Instagram (1:1)
- `clean`: No effects - clean video
- `dark`: Dark theme with enhanced shadows

## Data Flow

```
Idea Generated
  ↓
Hook Variants Created
  ↓
Record Once (or use input video)
  ↓
Optimize Retention (ScreenArc processing)
  ↓
Generate 20 Variants (with ScreenArc zoom effects)
  ↓
Export Per Platform
  ↓
Publish Staggered
  ↓
Collect Metrics
  ↓
Update Hook Weights
  ↓
Update Cluster Scores
  ↓
Recommend Next Topics
  ↓
Repeat
```

## Configuration

Edit `shared/config/settings.py` or set environment variables:

- `VCOS_API_KEY`: API authentication key
- `VCOS_DATA_ROOT`: Data directory path
- `VCOS_DATABASE_URL`: Database connection string

## Development

Each service is independently testable. Services communicate through:
- Shared schemas (`shared/schemas/`)
- Event bus (`shared/event_bus/`)
- Database (SQLite by default)

## Production Considerations

- Replace SQLite with PostgreSQL for production
- Use Redis for rate limiting and event bus
- Implement proper platform API integrations
- Add authentication/authorization
- Set up monitoring and alerting
- Use container orchestration (Kubernetes)
- Ensure ScreenArc CLI is available in production environment

## Integration Notes

- The `generation_content/` folder is preserved and integrated
- Recording functionality uses ScreenArc CLI via Python wrappers
- All services are designed for async operation
- Database schemas auto-initialize on first import
- ScreenArc integration handles errors gracefully with fallbacks

## License

See project root LICENSE file.
