#!/usr/bin/env python3
"""
Script to upload custom models to Hugging Face Hub.

INSTRUCTIONS:
1. Create a Hugging Face account at https://huggingface.co
2. Go to Settings > Access Tokens > Create new token (with Write permission)
3. Run: huggingface-cli login (paste your token when prompted)
4. Then run this script

This will upload:
- Subjectivity model → your-username/tourism-subjectivity-bert
- Categories model → your-username/tourism-categories-bert
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_folder

# ============ CONFIGURATION ============
# CHANGE THIS to your Hugging Face username!
HF_USERNAME = "victorwkey"

# Model names on Hugging Face
SUBJECTIVITY_REPO = f"{HF_USERNAME}/tourism-subjectivity-bert"
CATEGORIES_REPO = f"{HF_USERNAME}/tourism-categories-bert"

# Local model paths
BASE_DIR = Path(__file__).parent.parent / "python" / "models"
SUBJECTIVITY_PATH = BASE_DIR / "subjectivity_task" / "best_model"
CATEGORIES_PATH = BASE_DIR / "multilabel_task" / "best_model"
# =======================================


def check_login():
    """Check if user is logged in to Hugging Face"""
    api = HfApi()
    try:
        user_info = api.whoami()
        print(f"✅ Logged in as: {user_info['name']}")
        return user_info['name']
    except Exception:
        print("❌ Not logged in to Hugging Face!")
        print("\nPlease run: huggingface-cli login")
        print("Then paste your access token from https://huggingface.co/settings/tokens")
        sys.exit(1)


def create_model_card(model_type: str) -> str:
    """Generate a model card README for the model"""
    if model_type == "subjectivity":
        return """---
license: mit
language:
  - es
  - en
tags:
  - text-classification
  - subjectivity
  - tourism
  - bert
  - spanish
datasets:
  - custom
pipeline_tag: text-classification
---

# Tourism Opinion Subjectivity Classifier

A BERT-based model fine-tuned for classifying tourism reviews as **subjective** or **objective**.

## Model Description

This model was trained as part of the AI Tourism Opinion Analyzer project to detect subjectivity in customer reviews.

## Usage

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("victorwkey/tourism-subjectivity-bert")
model = AutoModelForSequenceClassification.from_pretrained("victorwkey/tourism-subjectivity-bert")

# Example
text = "El hotel tiene una piscina muy bonita"
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)
```

## Training

- Base model: BERT multilingual
- Task: Binary classification (subjective/objective)
- Dataset: Custom tourism reviews dataset
"""
    else:  # categories
        return """---
license: mit
language:
  - es
  - en
tags:
  - text-classification
  - multi-label-classification
  - tourism
  - bert
  - spanish
datasets:
  - custom
pipeline_tag: text-classification
---

# Tourism Opinion Category Classifier

A BERT-based model fine-tuned for multi-label classification of tourism reviews into categories.

## Model Description

This model was trained as part of the AI Tourism Opinion Analyzer project to classify customer reviews into multiple categories like: location, service, cleanliness, etc.

## Usage

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("victorwkey/tourism-categories-bert")
model = AutoModelForSequenceClassification.from_pretrained("victorwkey/tourism-categories-bert")

# Example
text = "La ubicación del hotel es excelente y el servicio fue muy amable"
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)
```

## Training

- Base model: BERT multilingual  
- Task: Multi-label classification
- Dataset: Custom tourism reviews dataset
- Categories: Location, Service, Cleanliness, Value, Amenities, etc.
"""


def upload_model(local_path: Path, repo_id: str, model_type: str):
    """Upload a model to Hugging Face Hub"""
    api = HfApi()
    
    print(f"\n📦 Uploading {model_type} model to: {repo_id}")
    
    # Check if local path exists
    if not local_path.exists():
        print(f"❌ Model path not found: {local_path}")
        return False
    
    # List files to upload
    files = list(local_path.iterdir())
    print(f"   Found {len(files)} files: {[f.name for f in files]}")
    
    # Create repository if it doesn't exist
    try:
        create_repo(repo_id, repo_type="model", exist_ok=True)
        print(f"   ✅ Repository created/verified: https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"   ⚠️ Could not create repo: {e}")
        return False
    
    # Create temporary README
    readme_path = local_path / "README.md"
    readme_existed = readme_path.exists()
    if not readme_existed:
        readme_content = create_model_card(model_type)
        readme_path.write_text(readme_content, encoding="utf-8")
        print("   📄 Created README.md model card")
    
    # Upload the folder
    try:
        upload_folder(
            folder_path=str(local_path),
            repo_id=repo_id,
            repo_type="model",
            commit_message=f"Upload {model_type} model"
        )
        print(f"   ✅ Upload complete!")
        print(f"   🔗 View at: https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        return False
    finally:
        # Clean up README if we created it
        if not readme_existed and readme_path.exists():
            readme_path.unlink()
    
    return True


def main():
    print("=" * 60)
    print("  Hugging Face Model Uploader")
    print("  AI Tourism Opinion Analyzer")
    print("=" * 60)
    
    # Check configuration
    if HF_USERNAME == "YOUR_USERNAME_HERE":
        print("\n❌ ERROR: Please edit this script and change HF_USERNAME")
        print("   to your Hugging Face username!")
        print("\n   Open: scripts/upload_models_to_hf.py")
        print("   Change: HF_USERNAME = \"YOUR_USERNAME_HERE\"")
        print("   To:     HF_USERNAME = \"your-actual-username\"")
        sys.exit(1)
    
    # Check login
    username = check_login()
    
    # Verify username matches
    if username.lower() != HF_USERNAME.lower():
        print(f"\n⚠️ Warning: You're logged in as '{username}' but HF_USERNAME is '{HF_USERNAME}'")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print(f"\n📁 Looking for models in: {BASE_DIR}")
    
    # Upload subjectivity model
    success1 = upload_model(SUBJECTIVITY_PATH, SUBJECTIVITY_REPO, "subjectivity")
    
    # Upload categories model
    success2 = upload_model(CATEGORIES_PATH, CATEGORIES_REPO, "categories")
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("  ✅ All models uploaded successfully!")
        print(f"\n  Your models are now available at:")
        print(f"  - https://huggingface.co/{SUBJECTIVITY_REPO}")
        print(f"  - https://huggingface.co/{CATEGORIES_REPO}")
    else:
        print("  ⚠️ Some uploads failed. Check the errors above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
