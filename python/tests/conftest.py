"""Shared fixtures for Python tests."""

import os
import sys
import tempfile
from pathlib import Path

import pytest
import pandas as pd

# Ensure the python/ directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def sample_df():
    """Minimal DataFrame mimicking the tourism dataset schema."""
    return pd.DataFrame(
        {
            "Titulo": ["Great hotel", "Bad experience", "Nice view", "Terrible food"],
            "Review": [
                "Room was clean and spacious",
                "Noise all night long",
                "Amazing ocean view from balcony",
                "The breakfast was awful",
            ],
            "Rating": [5, 1, 4, 2],
            "Fecha": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
            ),
            "Recomendacion": ["Si", "No", "Si", "No"],
        }
    )


@pytest.fixture
def sample_csv(sample_df, tmp_path):
    """Write the sample DataFrame to a CSV and return its path."""
    csv_path = tmp_path / "dataset.csv"
    sample_df.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def output_dir(tmp_path):
    """Create and return a temporary output directory."""
    out = tmp_path / "output"
    out.mkdir()
    return str(out)


@pytest.fixture(autouse=True)
def _patch_output_dir(tmp_path, monkeypatch):
    """Redirect OUTPUT_DIR to a temp folder so tests never write to real data."""
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "data"))
