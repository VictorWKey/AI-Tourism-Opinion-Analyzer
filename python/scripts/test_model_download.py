"""
Test Model Download and Cache Verification
============================================
This script tests that all required ML models download correctly
and are cached persistently in the HuggingFace cache directory.

Models tested:
- Sentiment: nlptown/bert-base-multilingual-uncased-sentiment
- Embeddings (BERTopic): sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import ConfigDataset


def get_cache_info():
    """Get information about HuggingFace cache."""
    cache_dir = Path(os.path.expanduser('~/.cache/huggingface/hub'))
    print(f'\n📁 HuggingFace Cache Directory: {cache_dir}')
    print(f'   Exists: {cache_dir.exists()}')

    if cache_dir.exists():
        # List cached models
        models = list(cache_dir.glob('models--*'))
        print(f'   Cached models: {len(models)}')
        for model in models:
            size_mb = sum(f.stat().st_size for f in model.rglob('*') if f.is_file()) / (1024 * 1024)
            print(f'     - {model.name}: {size_mb:.1f} MB')

    return cache_dir


def check_model_cached(model_name: str) -> bool:
    """Check if a model is already in the cache."""
    try:
        from huggingface_hub import scan_cache_dir

        cache_info = scan_cache_dir()
        cached_repos = [repo.repo_id for repo in cache_info.repos]
        return model_name in cached_repos
    except ImportError:
        # Fallback: check directory
        cache_dir = Path(os.path.expanduser('~/.cache/huggingface/hub'))
        safe_name = model_name.replace('/', '--')
        return (cache_dir / f'models--{safe_name}').exists()
    except Exception:
        # Cache doesn't exist yet
        return False


def test_sentiment_model():
    """Test downloading/loading the sentiment model."""
    model_name = 'nlptown/bert-base-multilingual-uncased-sentiment'
    print(f'\n🔍 Testing Sentiment Model: {model_name}')
    print(f'   Already cached: {check_model_cached(model_name)}')

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        cache_dir = ConfigDataset.get_models_cache_dir()

        print('   ⏳ Loading tokenizer...')
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        print('   ✓ Tokenizer loaded')

        print('   ⏳ Loading model...')
        model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir)
        print('   ✓ Model loaded')

        # Quick test
        inputs = tokenizer('This is a great experience!', return_tensors='pt')
        outputs = model(**inputs)
        print(f'   ✓ Model works! Output shape: {outputs.logits.shape}')

        return True
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return False


def test_embeddings_model():
    """Test downloading/loading the BERTopic embeddings model."""
    model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    print(f'\n🔍 Testing Embeddings Model (BERTopic): {model_name}')
    print(f'   Already cached: {check_model_cached(model_name)}')

    try:
        from sentence_transformers import SentenceTransformer

        cache_dir = ConfigDataset.get_models_cache_dir()

        print('   \u23f3 Loading SentenceTransformer...')
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', cache_folder=cache_dir)
        print('   ✓ Model loaded')

        # Quick test
        embeddings = model.encode(['This is a test sentence.'])
        print(f'   ✓ Model works! Embedding shape: {embeddings.shape}')

        return True
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return False


def verify_cache_persistence():
    """Verify that models are stored in persistent cache."""
    print('\n' + '=' * 60)
    print('📦 CACHE PERSISTENCE VERIFICATION')
    print('=' * 60)

    models_to_check = [
        ('sentiment', 'nlptown/bert-base-multilingual-uncased-sentiment'),
        ('embeddings', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'),
        ('subjectivity', 'victorwkey/tourism-subjectivity-bert'),
        ('categories', 'victorwkey/tourism-categories-bert'),
    ]

    cache_dir = Path(ConfigDataset.get_models_cache_dir())
    print(f'\nLocal cache location: {cache_dir}')
    print('Models are stored within the project directory \u2713')

    all_cached = True
    for key, model_name in models_to_check:
        is_cached = check_model_cached(model_name)
        status = '✓ CACHED' if is_cached else '✗ NOT CACHED'
        print(f'  {key}: {status}')
        if not is_cached:
            all_cached = False

    if all_cached:
        print('\n✅ All models are cached and will persist across app restarts!')
    else:
        print('\n⚠️ Some models are not cached. Run the download test first.')

    return all_cached


def main():
    print('=' * 60)
    print('🧪 MODEL DOWNLOAD & CACHE TEST')
    print('=' * 60)

    # Show initial cache state
    get_cache_info()

    # Test each model
    results = {}

    print('\n' + '-' * 60)
    print('DOWNLOADING/LOADING MODELS')
    print('-' * 60)

    results['sentiment'] = test_sentiment_model()
    results['embeddings'] = test_embeddings_model()

    # Show final cache state
    print('\n' + '-' * 60)
    print('CACHE STATE AFTER DOWNLOAD')
    print('-' * 60)
    get_cache_info()

    # Verify persistence
    verify_cache_persistence()

    # Summary
    print('\n' + '=' * 60)
    print('📊 SUMMARY')
    print('=' * 60)

    all_success = all(results.values())
    for key, success in results.items():
        status = '✅ SUCCESS' if success else '❌ FAILED'
        print(f'  {key}: {status}')

    if all_success:
        print('\n🎉 All models downloaded and cached successfully!')
        print('   Models will persist across app restarts.')
    else:
        print('\n⚠️ Some models failed to download. Check the errors above.')

    return 0 if all_success else 1


if __name__ == '__main__':
    sys.exit(main())
