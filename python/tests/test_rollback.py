"""Tests for RollbackManager."""

import pytest

from core.rollback_manager import RollbackManager


@pytest.fixture
def rollback_mgr(tmp_path, monkeypatch):
    """Create a RollbackManager pointing at a temp directory."""
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    monkeypatch.setenv('OUTPUT_DIR', str(tmp_path))
    mgr = RollbackManager()
    return mgr


class TestRollbackManager:
    """Unit tests for RollbackManager."""

    def test_generate_session_id_format(self, rollback_mgr):
        session_id = rollback_mgr._generate_session_id()
        assert session_id.startswith('session_')
        assert len(session_id) > 8

    def test_file_hash_empty_for_missing_file(self, rollback_mgr, tmp_path):
        result = rollback_mgr._get_file_hash(tmp_path / 'nonexistent.txt')
        assert result == ''

    def test_file_hash_deterministic(self, rollback_mgr, tmp_path):
        f = tmp_path / 'test.txt'
        f.write_text('hello world')
        h1 = rollback_mgr._get_file_hash(f)
        h2 = rollback_mgr._get_file_hash(f)
        assert h1 == h2
        assert len(h1) == 32  # MD5 hex digest

    def test_begin_phase_creates_backup(self, rollback_mgr, tmp_path):
        """begin_phase should create a backup session."""
        data_dir = rollback_mgr.data_dir
        data_dir.mkdir(exist_ok=True)
        # Create a file that phase 1 modifies
        csv = data_dir / 'dataset.csv'
        csv.write_text('col1,col2\n1,2\n')

        session_id = rollback_mgr.begin_phase(1)
        assert session_id is not None
        assert session_id.startswith('session_')
        assert rollback_mgr.get_active_session() == session_id

    def test_commit_clears_session(self, rollback_mgr, tmp_path):
        """commit should clean up the active session."""
        data_dir = rollback_mgr.data_dir
        data_dir.mkdir(exist_ok=True)
        csv = data_dir / 'dataset.csv'
        csv.write_text('col1,col2\n1,2\n')

        session_id = rollback_mgr.begin_phase(1)
        result = rollback_mgr.commit(session_id)
        assert result.get('success') is True
        assert rollback_mgr.get_active_session() is None

    def test_rollback_restores_original_file(self, rollback_mgr, tmp_path):
        """rollback should restore original file content."""
        data_dir = rollback_mgr.data_dir
        data_dir.mkdir(exist_ok=True)
        csv = data_dir / 'dataset.csv'
        original_content = 'col1,col2\n1,2\n'
        csv.write_text(original_content)

        session_id = rollback_mgr.begin_phase(1)

        # Simulate phase modifying the file
        csv.write_text('modified,data\n3,4\n')

        result = rollback_mgr.rollback(session_id)
        assert result.get('success') is True
        assert csv.read_text() == original_content

    def test_track_new_file_deleted_on_rollback(self, rollback_mgr, tmp_path):
        """Files tracked as new should be deleted on rollback."""
        data_dir = rollback_mgr.data_dir
        data_dir.mkdir(exist_ok=True)

        session_id = rollback_mgr.begin_phase(1)

        new_file = data_dir / 'new_output.json'
        new_file.write_text('{}')
        rollback_mgr.track_new_file(str(new_file))

        rollback_mgr.rollback(session_id)
        assert not new_file.exists()

    def test_phase_files_mapping_has_required_phases(self, rollback_mgr):
        """PHASE_FILES should cover all expected phases."""
        for phase_num in range(1, 9):
            assert phase_num in RollbackManager.PHASE_FILES

    def test_no_active_session_initially(self, rollback_mgr):
        assert rollback_mgr.get_active_session() is None
        assert rollback_mgr.get_active_phase() is None
