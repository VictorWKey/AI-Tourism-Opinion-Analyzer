"""Tests for fase_01_procesamiento_basico.py — ProcesadorBasico."""

import pandas as pd

from core.fase_01_procesamiento_basico import ProcesadorBasico


class TestProcesadorBasico:
    """Tests for the basic processing phase."""

    def test_creates_consolidado_from_titulo_and_review(self, sample_df):
        """crear_texto_consolidado should merge Titulo + Review."""
        proc = ProcesadorBasico.__new__(ProcesadorBasico)
        row = sample_df.iloc[0]
        result = proc.crear_texto_consolidado(row)
        assert 'Great hotel' in result
        assert 'Room was clean' in result

    def test_creates_consolidado_handles_nan(self):
        """crear_texto_consolidado should handle missing values."""
        proc = ProcesadorBasico.__new__(ProcesadorBasico)
        row = pd.Series({'Titulo': None, 'Review': 'Some review'})
        result = proc.crear_texto_consolidado(row)
        assert 'Some review' in result

    def test_procesar_creates_output_csv(self, sample_csv, tmp_path, monkeypatch):
        """procesar() should create a processed CSV with TituloReview column."""
        data_dir = tmp_path / 'data'
        data_dir.mkdir(exist_ok=True)

        # Copy sample CSV to the data directory
        import shutil

        dest = data_dir / 'dataset.csv'
        shutil.copy(sample_csv, str(dest))

        monkeypatch.setenv('OUTPUT_DIR', str(tmp_path))

        proc = ProcesadorBasico(input_path=str(dest))
        proc.procesar(forzar=True)

        # Output should contain TituloReview column (writes to dataset_path)
        output_path = proc.dataset_path
        assert output_path.exists(), f'Output CSV should exist at {output_path}'
        df_out = pd.read_csv(output_path)
        assert 'TituloReview' in df_out.columns

    def test_ya_procesado_returns_false_for_fresh_data(self, sample_csv, tmp_path, monkeypatch):
        """ya_procesado should return False when data hasn't been processed."""
        data_dir = tmp_path / 'data'
        data_dir.mkdir(exist_ok=True)
        import shutil

        dest = data_dir / 'dataset.csv'
        shutil.copy(sample_csv, str(dest))

        monkeypatch.setenv('OUTPUT_DIR', str(tmp_path))
        proc = ProcesadorBasico(input_path=str(dest))
        assert proc.ya_procesado() is False

    def test_ya_procesado_returns_true_after_processing(self, sample_csv, tmp_path, monkeypatch):
        """ya_procesado should return True after processing."""
        data_dir = tmp_path / 'data'
        data_dir.mkdir(exist_ok=True)
        import shutil

        dest = data_dir / 'dataset.csv'
        shutil.copy(sample_csv, str(dest))

        monkeypatch.setenv('OUTPUT_DIR', str(tmp_path))
        proc = ProcesadorBasico(input_path=str(dest))
        proc.procesar(forzar=True)
        assert proc.ya_procesado() is True

    def test_procesar_is_idempotent(self, sample_csv, tmp_path, monkeypatch):
        """Running procesar twice without forzar should be a no-op the second time."""
        data_dir = tmp_path / 'data'
        data_dir.mkdir(exist_ok=True)
        import shutil

        dest = data_dir / 'dataset.csv'
        shutil.copy(sample_csv, str(dest))

        monkeypatch.setenv('OUTPUT_DIR', str(tmp_path))
        proc = ProcesadorBasico(input_path=str(dest))
        proc.procesar(forzar=True)

        output_path = proc.dataset_path
        mtime1 = output_path.stat().st_mtime

        # Second run without forzar should skip
        proc2 = ProcesadorBasico(input_path=str(dest))
        proc2.procesar(forzar=False)

        mtime2 = proc.dataset_path.stat().st_mtime
        assert mtime1 == mtime2, 'File mtime should not change when already processed'
