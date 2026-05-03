#!/usr/bin/env bash
# scripts/setup_github_repo.sh
# ─────────────────────────────────────────────────────────────────────────────
# Run this ONCE from the project root to initialize git and push to GitHub.
# Prerequisites: git installed, GitHub CLI (gh) installed and authenticated.
#
# Usage:
#   chmod +x scripts/setup_github_repo.sh
#   ./scripts/setup_github_repo.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

REPO_NAME="health-conflict-detection"
REPO_DESC="ML-Based Multi-Source Health Record Conflict Detection for Karnataka's Rural CHW Ecosystem"
VISIBILITY="public"   # change to "private" if needed

echo "=========================================================="
echo "  Setting up GitHub repo: $REPO_NAME"
echo "=========================================================="

# 1. Initialize git
git init
git add .
git commit -m "feat: initial project scaffold with NFHS-5 dataset generator

- Folder structure for ingestion, preprocessing, conflict detection, resolution
- NFHS-5 Karnataka distribution parameters (karnataka_distributions.yaml)
- Synthetic dataset generator (scripts/generate_dataset.py)
- Hybrid conflict detector (rule-based + XGBoost)
- Confidence-weighted conflict resolver
- FastAPI + Streamlit stubs
- Pipeline config (configs/pipeline.yaml)"

# 2. Create GitHub repo via CLI
gh repo create "$REPO_NAME" \
  --description "$REPO_DESC" \
  --$VISIBILITY \
  --source=. \
  --remote=origin \
  --push

echo ""
echo "✅  Repository created and pushed!"
echo "    https://github.com/$(gh api user --jq .login)/$REPO_NAME"
echo ""
echo "Next steps:"
echo "  1. Install dependencies:  pip install -r requirements.txt"
echo "  2. Generate dataset:      python scripts/generate_dataset.py --n_patients 50000 --seed 42"
echo "  3. Run pipeline:          python scripts/run_pipeline.py --config configs/pipeline.yaml"
