"""
Rollback Manager for Pipeline State Recovery
==============================================
Manages backups and rollback operations for pipeline phases.
Ensures clean state recovery when operations are interrupted.
"""

import os
import shutil
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import threading


class RollbackManager:
    """
    Manages file backups and rollback operations for pipeline phases.
    
    Features:
    - Creates automatic backups before phase execution
    - Tracks newly created files during execution
    - Supports full rollback to pre-phase state
    - Cleans up backups after successful completion
    - Thread-safe for concurrent access
    """
    
    # Base paths - use ConfigDataset for dynamic resolution
    @classmethod
    def _get_data_dir(cls) -> Path:
        from config.config import ConfigDataset
        return ConfigDataset.get_data_dir()
    
    @property
    def data_dir(self) -> Path:
        return self._get_data_dir()
    
    @property
    def backup_dir(self) -> Path:
        return self.data_dir / ".backups"
    
    # Keep class-level references for backward compatibility
    DATA_DIR = Path(__file__).parent.parent / "data"
    BACKUP_DIR = DATA_DIR / ".backups"
    
    # Known files modified by each phase
    PHASE_FILES: Dict[int, List[str]] = {
        1: ["dataset.csv"],
        2: ["dataset.csv"],
        3: ["dataset.csv"],
        4: ["dataset.csv"],
        5: ["dataset.csv", "shared/categorias_scores.json"],
        6: ["dataset.csv"],
        7: ["shared/resumenes.json"],
        8: [],  # Phase 8 creates files in visualizaciones/
    }
    
    # Directories created by phases (for cleanup on rollback)
    PHASE_DIRS: Dict[int, List[str]] = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: ["shared"],
        6: [],
        7: ["shared"],
        8: ["visualizaciones"],
    }
    
    def __init__(self):
        self._lock = threading.Lock()
        self._active_session: Optional[str] = None
        self._tracked_new_files: Set[str] = set()
        self._backup_manifest: Dict[str, str] = {}
        self._session_phase: Optional[int] = None
        # Override class-level paths with dynamic resolution
        self.DATA_DIR = self._get_data_dir()
        self.BACKUP_DIR = self.DATA_DIR / ".backups"
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID based on timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"session_{timestamp}"
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for integrity verification."""
        if not file_path.exists():
            return ""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _get_backup_path(self, original_path: str, session_id: str) -> Path:
        """Get backup file path for a given original path."""
        # Flatten path structure for backup
        safe_name = original_path.replace("/", "__").replace("\\", "__")
        return self.BACKUP_DIR / session_id / safe_name
    
    def begin_phase(self, phase: int) -> str:
        """
        Begin a new phase execution session.
        Creates backups of all files that may be modified by this phase.
        
        Args:
            phase: Phase number (1-7)
            
        Returns:
            Session ID for this execution
        """
        with self._lock:
            # Generate session ID
            session_id = self._generate_session_id()
            self._active_session = session_id
            self._session_phase = phase
            self._tracked_new_files.clear()
            self._backup_manifest.clear()
            
            # Create backup directory
            session_backup_dir = self.BACKUP_DIR / session_id
            session_backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup files that may be modified
            files_to_backup = self.PHASE_FILES.get(phase, [])
            
            for relative_path in files_to_backup:
                original_path = self.DATA_DIR / relative_path
                if original_path.exists():
                    backup_path = self._get_backup_path(relative_path, session_id)
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(original_path, backup_path)
                    self._backup_manifest[relative_path] = self._get_file_hash(original_path)
            
            # For phase 8, snapshot the visualizaciones directory state
            if phase == 8:
                viz_dir = self.DATA_DIR / "visualizaciones"
                if viz_dir.exists():
                    # Record all existing files
                    for item in viz_dir.rglob("*"):
                        if item.is_file():
                            rel_path = str(item.relative_to(self.DATA_DIR))
                            backup_path = self._get_backup_path(rel_path, session_id)
                            backup_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, backup_path)
                            self._backup_manifest[rel_path] = self._get_file_hash(item)
            
            # Save manifest
            manifest_path = session_backup_dir / "manifest.json"
            manifest_data = {
                "session_id": session_id,
                "phase": phase,
                "timestamp": datetime.now().isoformat(),
                "backed_up_files": self._backup_manifest,
                "new_files": [],  # Will be updated on rollback/commit
            }
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=2)
            
            return session_id
    
    def track_new_file(self, file_path: str) -> None:
        """
        Track a newly created file during phase execution.
        These files will be deleted on rollback.
        
        Args:
            file_path: Path to the newly created file (relative to data dir)
        """
        with self._lock:
            if self._active_session:
                # Convert to relative path if absolute
                path = Path(file_path)
                if path.is_absolute():
                    try:
                        path = path.relative_to(self.DATA_DIR)
                    except ValueError:
                        pass  # Keep as-is if not relative to DATA_DIR
                self._tracked_new_files.add(str(path))
    
    def rollback(self, session_id: Optional[str] = None) -> Dict[str, any]:
        """
        Rollback to pre-phase state.
        Restores backed up files and deletes newly created files.
        
        Args:
            session_id: Session to rollback (uses active session if None)
            
        Returns:
            Dictionary with rollback results
        """
        with self._lock:
            target_session = session_id or self._active_session
            
            if not target_session:
                return {"success": False, "error": "No active session to rollback"}
            
            session_backup_dir = self.BACKUP_DIR / target_session
            
            if not session_backup_dir.exists():
                return {"success": False, "error": f"Backup session not found: {target_session}"}
            
            results = {
                "success": True,
                "restored_files": [],
                "deleted_files": [],
                "errors": []
            }
            
            try:
                # Load manifest
                manifest_path = session_backup_dir / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                else:
                    manifest = {"backed_up_files": {}}
                
                phase = manifest.get("phase", self._session_phase)
                
                # Step 1: Delete newly created files
                for new_file in self._tracked_new_files:
                    file_path = self.DATA_DIR / new_file
                    if file_path.exists():
                        try:
                            file_path.unlink()
                            results["deleted_files"].append(str(new_file))
                        except Exception as e:
                            results["errors"].append(f"Failed to delete {new_file}: {e}")
                
                # Step 2: For phase 8, delete all visualizaciones subdirectories created
                if phase == 8:
                    viz_dir = self.DATA_DIR / "visualizaciones"
                    if viz_dir.exists():
                        # Get list of backed up files
                        backed_up = set(manifest.get("backed_up_files", {}).keys())
                        
                        # Delete files not in backup
                        for item in list(viz_dir.rglob("*")):
                            if item.is_file():
                                rel_path = str(item.relative_to(self.DATA_DIR))
                                if rel_path not in backed_up:
                                    try:
                                        item.unlink()
                                        results["deleted_files"].append(rel_path)
                                    except Exception as e:
                                        results["errors"].append(f"Failed to delete {rel_path}: {e}")
                        
                        # Clean up empty directories
                        for subdir in list(viz_dir.iterdir()):
                            if subdir.is_dir():
                                try:
                                    if not any(subdir.iterdir()):
                                        subdir.rmdir()
                                except Exception:
                                    pass
                
                # Step 3: Restore backed up files
                for relative_path, original_hash in manifest.get("backed_up_files", {}).items():
                    backup_path = self._get_backup_path(relative_path, target_session)
                    original_path = self.DATA_DIR / relative_path
                    
                    if backup_path.exists():
                        try:
                            # Ensure parent directory exists
                            original_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(backup_path, original_path)
                            results["restored_files"].append(relative_path)
                        except Exception as e:
                            results["errors"].append(f"Failed to restore {relative_path}: {e}")
                
                # Step 4: Cleanup backup directory
                try:
                    shutil.rmtree(session_backup_dir)
                except Exception as e:
                    results["errors"].append(f"Failed to cleanup backup: {e}")
                
                # Clear session state
                if target_session == self._active_session:
                    self._active_session = None
                    self._session_phase = None
                    self._tracked_new_files.clear()
                    self._backup_manifest.clear()
                
                if results["errors"]:
                    results["success"] = False
                
                return results
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "restored_files": results.get("restored_files", []),
                    "deleted_files": results.get("deleted_files", [])
                }
    
    def commit(self, session_id: Optional[str] = None) -> Dict[str, any]:
        """
        Commit phase execution - cleanup backups as phase completed successfully.
        
        Args:
            session_id: Session to commit (uses active session if None)
            
        Returns:
            Dictionary with commit results
        """
        with self._lock:
            target_session = session_id or self._active_session
            
            if not target_session:
                return {"success": True, "message": "No active session"}
            
            session_backup_dir = self.BACKUP_DIR / target_session
            
            try:
                # Remove backup directory
                if session_backup_dir.exists():
                    shutil.rmtree(session_backup_dir)
                
                # Clear session state
                if target_session == self._active_session:
                    self._active_session = None
                    self._session_phase = None
                    self._tracked_new_files.clear()
                    self._backup_manifest.clear()
                
                return {"success": True, "message": "Session committed"}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    def get_active_session(self) -> Optional[str]:
        """Get the current active session ID."""
        return self._active_session
    
    def get_active_phase(self) -> Optional[int]:
        """Get the current active phase number."""
        return self._session_phase
    
    def find_pending_session(self) -> Optional[str]:
        """
        Find the most recent pending session that was not committed.
        Used after a crash/kill to find sessions that need rollback.
        
        Returns:
            Session ID if found, None otherwise
        """
        if not self.BACKUP_DIR.exists():
            return None
        
        # Find all session directories
        sessions = []
        for session_dir in self.BACKUP_DIR.iterdir():
            if session_dir.is_dir() and session_dir.name.startswith("session_"):
                manifest_path = session_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                        timestamp_str = manifest.get("timestamp", "")
                        if timestamp_str:
                            sessions.append((session_dir.name, timestamp_str))
                    except Exception:
                        pass
        
        if not sessions:
            return None
        
        # Sort by timestamp (most recent first) and return the most recent
        sessions.sort(key=lambda x: x[1], reverse=True)
        return sessions[0][0]
    
    def rollback_pending(self) -> Dict[str, any]:
        """
        Find and rollback any pending session.
        Used after a crash/kill to restore the previous state.
        
        Returns:
            Dictionary with rollback results
        """
        pending_session = self.find_pending_session()
        
        if not pending_session:
            return {"success": True, "message": "No pending session to rollback"}
        
        return self.rollback(pending_session)
    
    def cleanup_old_backups(self, max_age_hours: int = 24) -> int:
        """
        Clean up old backup sessions that may have been left behind.
        
        Args:
            max_age_hours: Maximum age of backups to keep
            
        Returns:
            Number of sessions cleaned up
        """
        if not self.BACKUP_DIR.exists():
            return 0
        
        cleaned = 0
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)
        
        for session_dir in self.BACKUP_DIR.iterdir():
            if session_dir.is_dir() and session_dir.name.startswith("session_"):
                manifest_path = session_dir / "manifest.json"
                try:
                    if manifest_path.exists():
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                        timestamp_str = manifest.get("timestamp", "")
                        if timestamp_str:
                            session_time = datetime.fromisoformat(timestamp_str)
                            if session_time.timestamp() < cutoff:
                                shutil.rmtree(session_dir)
                                cleaned += 1
                                continue
                    
                    # If no valid manifest, check directory modification time
                    if session_dir.stat().st_mtime < cutoff:
                        shutil.rmtree(session_dir)
                        cleaned += 1
                        
                except Exception:
                    pass  # Skip problematic directories
        
        return cleaned


# Global instance for use across the application
_rollback_manager: Optional[RollbackManager] = None


def get_rollback_manager() -> RollbackManager:
    """Get or create the global RollbackManager instance."""
    global _rollback_manager
    if _rollback_manager is None:
        _rollback_manager = RollbackManager()
    return _rollback_manager
