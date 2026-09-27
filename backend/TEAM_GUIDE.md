# Team Guide

## Repository layout

Keep the same Git repository:

```text
GramMausam/
├── frontend/
└── backend/
```

Do not create another repository for the backend unless the team explicitly decides to split deployment later.

## Suggested ownership

### Data / GIS

Work mainly in:

```text
backend/app/geo/
backend/app/data/
data/raw/
data/processed/
scripts/validate_dataset.py
```

Responsibilities:

- source and document datasets
- clean and align spatial data
- verify CRS
- prepare block and Panchayat boundaries
- build fine-resolution grids
- prepare model-ready features

### ML

Work mainly in:

```text
backend/app/ml/
scripts/train_models.py
scripts/evaluate_models.py
```

Responsibilities:

- baseline method
- feature engineering
- model selection
- training
- validation
- error analysis
- saved model artifacts

Do not report demo/synthetic model metrics as real results.

### API / Integration

Work mainly in:

```text
backend/app/api/
backend/app/services/
backend/app/main.py
```

Responsibilities:

- endpoint design
- validation
- API response shapes
- frontend integration
- CORS configuration

## Git workflow

Pull before starting:

```bash
git pull origin main
```

Create a feature branch for larger work:

```bash
git checkout -b feature/downscaling-model
```

Commit small, meaningful changes:

```bash
git add .
git commit -m "add rainfall downscaling model"
```

Push the branch:

```bash
git push -u origin feature/downscaling-model
```

For small coordinated changes on `main`, pull before pushing to avoid rejected pushes.

## Rules

1. Never commit `.env` files or credentials.
2. Never hardcode database passwords or API tokens.
3. Do not add OpenAI/ChatGPT API keys to the project.
4. Do not commit raw datasets unless their licence and repository policy allow it.
5. Keep scientific/model logic in backend code, not in React components.
6. Do not claim model accuracy until it has been evaluated on an appropriate held-out real dataset.
