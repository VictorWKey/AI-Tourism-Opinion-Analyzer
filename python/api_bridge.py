"""
JSON API Bridge for Electron Communication
==========================================
Provides a JSON-based interface for the pipeline.
Communicates via stdin/stdout with JSON messages.
"""

import sys
import json
import traceback
import io
import os
import signal
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from contextlib import contextmanager

# Configure logging for the pipeline
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # Log to stderr to not interfere with JSON
    ]
)
logger = logging.getLogger(__name__)

# Track if full pipeline is available
PIPELINE_AVAILABLE = False
PIPELINE_ERROR = None
ROLLBACK_AVAILABLE = False

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Try to import rollback manager
try:
    from core.rollback_manager import get_rollback_manager, RollbackManager
    ROLLBACK_AVAILABLE = True
except ImportError:
    get_rollback_manager = None
    RollbackManager = None

# Try to import pipeline components
try:
    import pandas as pd
    from core import (
        ProcesadorBasico,
        AnalizadorSentimientos,
        AnalizadorSubjetividad,
        ClasificadorCategorias,
        AnalizadorJerarquicoTopicos,
        ResumidorInteligente,
        GeneradorVisualizaciones,
        LLMProvider
    )
    PIPELINE_AVAILABLE = True
except ImportError as e:
    PIPELINE_ERROR = str(e)
    # Create placeholder classes for when pipeline is not available
    pd = None
    ProcesadorBasico = None
    AnalizadorSentimientos = None
    AnalizadorSubjetividad = None
    ClasificadorCategorias = None
    AnalizadorJerarquicoTopicos = None
    ResumidorInteligente = None
    GeneradorVisualizaciones = None
    LLMProvider = None



class ProgressReporter:
    """Reports progress back to Electron via stdout."""
    
    def __init__(self, phase: int, phase_name: str):
        self.phase = phase
        self.phase_name = phase_name
        self.last_reported = 0
    
    def report(self, progress: int, message: str = ""):
        """Send progress update to Electron."""
        # Avoid sending duplicate progress updates
        if progress == self.last_reported and message == "":
            return
        
        self.last_reported = progress
        response = {
            "type": "progress",
            "phase": self.phase,
            "phaseName": self.phase_name,
            "progress": progress,
            "message": message
        }
        # Save and restore stdout to ensure JSON goes to real stdout
        old_stdout = sys.stdout
        sys.stdout = sys.__stdout__
        print(json.dumps(response), flush=True)
        sys.stdout = old_stdout


class TqdmProgressCapture:
    """Capture tqdm progress and convert to progress updates."""
    
    def __init__(self, reporter: ProgressReporter):
        self.reporter = reporter
        self.old_stderr = None
        
    def __enter__(self):
        """Enable tqdm progress capture."""
        # Set environment variable to enable our custom tqdm callback
        os.environ['TQDM_DISABLE'] = '0'
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup."""
        pass
    
    def parse_tqdm_line(self, line: str):
        """Parse tqdm progress line and report progress."""
        if 'Progreso:' in line and '%|' in line:
            try:
                # Extract percentage from tqdm output
                # Format: "Progreso:  42%|████▏     | 205/483 [00:01<00:01, 154.06it/s]"
                percent_part = line.split('Progreso:')[1].split('%')[0].strip()
                progress = int(float(percent_part))
                
                # Extract current/total if available
                if '|' in line and '/' in line:
                    parts = line.split('|')[1].split('[')[0].strip().split('/')
                    if len(parts) == 2:
                        current = parts[0].strip()
                        total = parts[1].strip().split()[0]
                        message = f"Procesando {current}/{total}"
                        self.reporter.report(progress, message)
                    else:
                        self.reporter.report(progress)
                else:
                    self.reporter.report(progress)
            except (ValueError, IndexError) as e:
                # If parsing fails, just ignore
                pass


@contextmanager
def redirect_stdout_to_stderr():
    """
    Context manager to redirect stdout to stderr.
    This prevents pipeline print statements from breaking JSON communication.
    """
    old_stdout = sys.stdout
    try:
        sys.stdout = sys.stderr
        yield
    finally:
        sys.stdout = old_stdout


class PipelineAPI:
    """JSON API for the analysis pipeline."""
    
    def __init__(self):
        self.current_phase = None
        self.should_stop = False
        self._current_session_id: Optional[str] = None
        
        # Initialize rollback manager if available
        self.rollback_manager = get_rollback_manager() if ROLLBACK_AVAILABLE else None
        
        # Build phases dictionary only if pipeline is available
        if PIPELINE_AVAILABLE:
            self.PHASES = {
                1: ("Procesamiento Básico", ProcesadorBasico),
                2: ("Análisis de Sentimientos", AnalizadorSentimientos),
                3: ("Análisis de Subjetividad", AnalizadorSubjetividad),
                4: ("Clasificación de Categorías", ClasificadorCategorias),
                5: ("Análisis Jerárquico de Tópicos", AnalizadorJerarquicoTopicos),
                6: ("Resumen Inteligente", ResumidorInteligente),
                7: ("Generación de Visualizaciones", GeneradorVisualizaciones),
            }
        else:
            self.PHASES = {
                1: ("Procesamiento Básico", None),
                2: ("Análisis de Sentimientos", None),
                3: ("Análisis de Subjetividad", None),
                4: ("Clasificación de Categorías", None),
                5: ("Análisis Jerárquico de Tópicos", None),
                6: ("Resumen Inteligente", None),
                7: ("Generación de Visualizaciones", None),
            }
    
    def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a pipeline command and return JSON response."""
        try:
            action = command.get("action")
            
            handlers = {
                "run_phase": self._run_phase,
                "run_all": self._run_all,
                "stop": self._stop,
                "stop_and_rollback": self._stop_and_rollback,
                "rollback": self._rollback,
                "get_status": self._get_status,
                "validate_dataset": self._validate_dataset,
                "validate_phase_dependencies": self._validate_phase_dependencies,
                "get_llm_info": self._get_llm_info,
                "check_ollama": self._check_ollama,
                "ping": self._ping,
                "check_pipeline": self._check_pipeline,
                "check_models_status": self._check_models_status,
                "download_models": self._download_models,
                "download_model": self._download_model,
                "get_download_size": self._get_download_size,
            }
            
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            return handler(command)
            
        except Exception as e:
            # On any exception, try to rollback if we have an active session
            if self.rollback_manager and self._current_session_id:
                self.rollback_manager.rollback(self._current_session_id)
                self._current_session_id = None
            
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _ping(self, command: Dict) -> Dict:
        """Health check endpoint."""
        return {
            "success": True, 
            "message": "pong", 
            "status": "ready",
            "pipelineAvailable": PIPELINE_AVAILABLE
        }
    
    def _check_pipeline(self, command: Dict) -> Dict:
        """Check if full pipeline is available."""
        return {
            "success": True,
            "available": PIPELINE_AVAILABLE,
            "error": PIPELINE_ERROR if not PIPELINE_AVAILABLE else None
        }
    
    def _run_phase(self, command: Dict) -> Dict:
        """Run a specific pipeline phase with rollback support."""
        if not PIPELINE_AVAILABLE:
            return {
                "success": False, 
                "error": f"Pipeline not available: {PIPELINE_ERROR}"
            }
        
        phase = command.get("phase")
        config = command.get("config", {})
        force = config.get("force", True)
        
        if phase not in self.PHASES:
            return {"success": False, "error": f"Invalid phase: {phase}"}
        
        phase_name, phase_class = self.PHASES[phase]
        reporter = ProgressReporter(phase, phase_name)
        
        self.current_phase = phase
        self.should_stop = False
        reporter.report(0, "Iniciando fase...")
        
        # Begin rollback session before phase execution
        session_id = None
        if self.rollback_manager:
            session_id = self.rollback_manager.begin_phase(phase)
            self._current_session_id = session_id
        
        try:
            # Redirect stdout to stderr to prevent pipeline print statements
            # from breaking JSON communication
            with redirect_stdout_to_stderr():
                # Check for stop signal before starting
                if self.should_stop:
                    raise InterruptedError("Phase stopped by user before execution")
                
                # Instantiate and run phase
                processor = phase_class()
                
                # Special handling for phases with custom parameters
                if phase == 6:
                    processor = ResumidorInteligente(
                        top_n_subtopicos=config.get("top_n_subtopicos", 3),
                        incluir_neutros=config.get("incluir_neutros", False)
                    )
                    processor.procesar(
                        tipos_resumen=config.get("tipos_resumen", 
                            ["descriptivo", "estructurado", "insights"]),
                        forzar=force
                    )
                else:
                    processor.procesar(forzar=force)
                
                # Check for stop signal after completion
                if self.should_stop:
                    raise InterruptedError("Phase stopped by user during execution")
            
            # Phase completed successfully - commit the session (cleanup backups)
            if self.rollback_manager and session_id:
                self.rollback_manager.commit(session_id)
                self._current_session_id = None
            
            reporter.report(100, "Fase completada")
            
            # Build output paths - these are relative to the Python working directory (python/)
            # which is where the phases save their outputs
            output_paths = {
                "datasetPath": "data/dataset.csv",
                "chartsPath": "data/visualizaciones",
                "summaryPath": "data/shared/resumen_analisis.json",
            }
            
            return {
                "success": True,
                "phase": phase,
                "phaseName": phase_name,
                "status": "completed",
                "outputs": output_paths
            }
            
        except InterruptedError as e:
            # User requested stop - rollback changes
            rollback_result = None
            if self.rollback_manager and session_id:
                rollback_result = self.rollback_manager.rollback(session_id)
                self._current_session_id = None
            
            return {
                "success": False,
                "phase": phase,
                "phaseName": phase_name,
                "status": "stopped",
                "error": str(e),
                "rollback": rollback_result
            }
            
        except Exception as e:
            # Error occurred - rollback changes
            rollback_result = None
            if self.rollback_manager and session_id:
                rollback_result = self.rollback_manager.rollback(session_id)
                self._current_session_id = None
            
            return {
                "success": False,
                "phase": phase,
                "phaseName": phase_name,
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "rollback": rollback_result
            }
        finally:
            self.current_phase = None
    
    def _run_all(self, command: Dict) -> Dict:
        """Run all pipeline phases sequentially."""
        config = command.get("config", {})
        phases_config = config.get("phases", {})
        results = []
        
        for phase in range(1, 8):
            if self.should_stop:
                # Add remaining phases as stopped
                for remaining_phase in range(phase, 8):
                    results.append({
                        "phase": remaining_phase,
                        "status": "stopped",
                        "success": False
                    })
                break
            
            # Check if phase is enabled (default to True)
            phase_key = f"phase{phase:02d}"
            phase_config = phases_config.get(phase_key, {"enabled": True})
            
            if not phase_config.get("enabled", True):
                results.append({
                    "phase": phase,
                    "status": "skipped"
                })
                continue
            
            result = self._run_phase({"phase": phase, "config": config})
            results.append(result)
            
            if not result["success"]:
                break
        
        self.should_stop = False
        
        return {
            "success": all(r.get("success", False) or r.get("status") == "skipped" 
                          for r in results),
            "results": results
        }
    
    def _stop(self, command: Dict) -> Dict:
        """Stop the current execution (without rollback)."""
        self.should_stop = True
        return {"success": True, "message": "Stop signal sent"}
    
    def _stop_and_rollback(self, command: Dict) -> Dict:
        """Stop execution and rollback any partial changes."""
        self.should_stop = True
        
        rollback_result = None
        if self.rollback_manager and self._current_session_id:
            rollback_result = self.rollback_manager.rollback(self._current_session_id)
            self._current_session_id = None
        
        return {
            "success": True, 
            "message": "Stop signal sent with rollback",
            "rollback": rollback_result,
            "rollbackPerformed": rollback_result is not None
        }
    
    def _rollback(self, command: Dict) -> Dict:
        """
        Manually trigger rollback for the current or specified session.
        If no session is specified and no active session exists, 
        tries to find and rollback any pending session (used after crash/kill).
        """
        session_id = command.get("session_id", self._current_session_id)
        
        if not self.rollback_manager:
            return {"success": False, "error": "Rollback manager not available"}
        
        # If no specific session, try to find a pending one (after crash/kill)
        if not session_id:
            result = self.rollback_manager.rollback_pending()
            return {
                "success": result.get("success", False),
                "rollback": result
            }
        
        result = self.rollback_manager.rollback(session_id)
        if session_id == self._current_session_id:
            self._current_session_id = None
        
        return {
            "success": result.get("success", False),
            "rollback": result
        }
    
    def _get_status(self, command: Dict) -> Dict:
        """Get current pipeline status."""
        return {
            "success": True,
            "currentPhase": self.current_phase,
            "isRunning": self.current_phase is not None
        }
    
    def _validate_dataset(self, command: Dict) -> Dict:
        """Validate a dataset file."""
        path = command.get("path")
        
        if not path or not Path(path).exists():
            return {"success": False, "error": "File not found"}
        
        # Check if pandas is available
        if pd is None:
            return {
                "success": False, 
                "error": "pandas not available. Install dependencies first."
            }
        
        try:
            df = pd.read_csv(path)
            
            # Check required columns - support multiple formats
            # Format 1: Original (Titulo, Review, FechaEstadia, Calificacion)
            # Format 2: Processed with combined title (TituloReview, FechaEstadia, Calificacion)
            # Format 3: Fully processed (TituloReview, FechaEstadia, Calificacion, Sentimiento, etc.)
            
            has_titulo_review = "TituloReview" in df.columns
            has_titulo = "Titulo" in df.columns
            has_review = "Review" in df.columns
            has_fecha = "FechaEstadia" in df.columns
            has_calificacion = "Calificacion" in df.columns
            
            # Determine what format we have
            if has_titulo_review and has_fecha and has_calificacion:
                # Valid: processed format
                required = ["TituloReview", "FechaEstadia", "Calificacion"]
                missing = []
            elif (has_titulo or has_review) and has_fecha and has_calificacion:
                # Valid: original format
                required = ["FechaEstadia", "Calificacion"]
                if has_titulo:
                    required.insert(0, "Titulo")
                if has_review:
                    required.insert(1 if has_titulo else 0, "Review")
                missing = []
            else:
                # Invalid: missing critical columns
                required = ["TituloReview or (Titulo and/or Review)", "FechaEstadia", "Calificacion"]
                missing = [col for col in ["FechaEstadia", "Calificacion"] if col not in df.columns]
                if not has_titulo_review and not has_titulo and not has_review:
                    missing.insert(0, "TituloReview or Titulo/Review")
            
            # Generate preview data
            preview = df.head(5).to_dict(orient="records")
            
            # Convert any NaN values to None for JSON serialization
            for row in preview:
                for key, value in row.items():
                    if pd.isna(value):
                        row[key] = None
            
            return {
                "success": True,
                "valid": len(missing) == 0,
                "rowCount": len(df),
                "columns": list(df.columns),
                "missingColumns": missing,
                "preview": preview,
                "alreadyProcessed": has_titulo_review
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_phase_dependencies(self, command: Dict) -> Dict:
        """
        Check if a phase has all required dependencies (previous phases completed).
        Returns which columns/files are missing and which phases need to be run.
        """
        phase = command.get("phase")
        dataset_path = command.get("dataset_path", "data/dataset.csv")
        
        # Phase dependencies mapping
        PHASE_DEPENDENCIES = {
            1: {
                "name": "Procesamiento Básico",
                "required_columns": [],
                "required_files": [],
                "depends_on_phases": []
            },
            2: {
                "name": "Análisis de Sentimientos",
                "required_columns": ["TituloReview"],
                "required_files": [],
                "depends_on_phases": [1]
            },
            3: {
                "name": "Análisis de Subjetividad",
                "required_columns": ["TituloReview"],
                "required_files": [],
                "depends_on_phases": [1]
            },
            4: {
                "name": "Clasificación de Categorías",
                "required_columns": ["TituloReview"],
                "required_files": [],
                "depends_on_phases": [1]
            },
            5: {
                "name": "Análisis Jerárquico de Tópicos",
                "required_columns": ["TituloReview", "Sentimiento", "Categorias"],
                "required_files": [],
                "depends_on_phases": [1, 2, 4]
            },
            6: {
                "name": "Resumen Inteligente",
                "required_columns": ["TituloReview", "Sentimiento", "Subjetividad", "Categorias"],
                "required_files": ["data/shared/categorias_scores.json"],
                "depends_on_phases": [1, 2, 3, 4]
            },
            7: {
                "name": "Visualizaciones",
                "required_columns": ["TituloReview", "Sentimiento", "Subjetividad", "Categorias", "Topico"],
                "required_files": [],
                "depends_on_phases": [1, 2, 3, 4, 5]
            }
        }
        
        if phase not in PHASE_DEPENDENCIES:
            return {"success": False, "error": f"Invalid phase: {phase}"}
        
        deps = PHASE_DEPENDENCIES[phase]
        missing_columns = []
        missing_files = []
        missing_phases = []
        
        # Check if dataset exists
        if not Path(dataset_path).exists():
            return {
                "success": True,
                "valid": False,
                "error": "Dataset no encontrado. Por favor carga un archivo CSV primero.",
                "missingColumns": [],
                "missingFiles": [],
                "missingPhases": deps["depends_on_phases"],
                "canRun": False
            }
        
        try:
            # Check required columns
            if deps["required_columns"]:
                df = pd.read_csv(dataset_path)
                for col in deps["required_columns"]:
                    if col not in df.columns:
                        missing_columns.append(col)
            
            # Check required files (resolve paths relative to dataset directory)
            dataset_dir = Path(dataset_path).parent
            for file_path in deps["required_files"]:
                # If path starts with data/, resolve relative to dataset directory
                if file_path.startswith("data/"):
                    # Remove 'data/' prefix and resolve from dataset parent
                    relative_path = file_path.replace("data/", "", 1)
                    full_path = dataset_dir / relative_path
                else:
                    full_path = Path(file_path)
                
                if not full_path.exists():
                    missing_files.append(file_path)
            
            # Determine missing phases based on missing columns/files
            if missing_columns or missing_files:
                # Map columns to phases
                column_to_phase = {
                    "TituloReview": 1,
                    "Sentimiento": 2,
                    "Subjetividad": 3,
                    "Categorias": 4,
                    "Topico": 5
                }
                
                for col in missing_columns:
                    phase_num = column_to_phase.get(col)
                    if phase_num and phase_num not in missing_phases:
                        missing_phases.append(phase_num)
                
                # If files are missing, add their respective phases
                if "categorias_embeddings.pkl" in str(missing_files):
                    if 4 not in missing_phases:
                        missing_phases.append(4)
                if "categorias_scores.json" in str(missing_files):
                    if 4 not in missing_phases:
                        missing_phases.append(4)
            
            # Build user-friendly message
            can_run = len(missing_columns) == 0 and len(missing_files) == 0
            error_message = None
            
            if not can_run:
                phase_names = {
                    1: "Fase 1: Procesamiento Básico",
                    2: "Fase 2: Análisis de Sentimientos",
                    3: "Fase 3: Análisis de Subjetividad",
                    4: "Fase 4: Clasificación de Categorías",
                    5: "Fase 5: Análisis de Tópicos"
                }
                
                missing_phase_names = [phase_names[p] for p in sorted(missing_phases) if p in phase_names]
                
                if missing_phase_names:
                    error_message = (
                        f"Esta fase requiere que ejecutes primero:\n\n" +
                        "\n".join(f"• {name}" for name in missing_phase_names)
                    )
                else:
                    error_message = "Faltan datos necesarios para ejecutar esta fase."
            
            return {
                "success": True,
                "valid": can_run,
                "canRun": can_run,
                "missingColumns": missing_columns,
                "missingFiles": missing_files,
                "missingPhases": sorted(missing_phases),
                "error": error_message
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error validating dependencies: {str(e)}"
            }
    
    def _get_llm_info(self, command: Dict) -> Dict:
        """Get LLM configuration info."""
        try:
            # Try to get info from LLMProvider if method exists
            if hasattr(LLMProvider, 'get_info'):
                info = LLMProvider.get_info()
                return {"success": True, **info}
            else:
                # Return basic info
                return {
                    "success": True,
                    "provider": "ollama",
                    "model": "llama3.2",
                    "configured": True
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_ollama(self, command: Dict) -> Dict:
        """Check Ollama availability."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.ok:
                data = response.json()
                return {
                    "success": True,
                    "running": True,
                    "models": [m["name"] for m in data.get("models", [])]
                }
            return {"success": True, "running": False, "models": []}
        except Exception:
            return {"success": True, "running": False, "models": []}

    def _check_models_status(self, command: Dict) -> Dict:
        """Check which ML models are already downloaded."""
        status = {
            "sentiment": False,
            "embeddings": False,
            "subjectivity": False,
            "categories": False,
        }
        
        try:
            # Check HuggingFace cache for transformer models
            try:
                from huggingface_hub import scan_cache_dir
                cache_info = scan_cache_dir()
                cached_repos = [repo.repo_id for repo in cache_info.repos]
                
                status["sentiment"] = "nlptown/bert-base-multilingual-uncased-sentiment" in cached_repos
                status["embeddings"] = "sentence-transformers/all-MiniLM-L6-v2" in cached_repos
            except ImportError:
                # huggingface_hub not available, try alternative check
                from pathlib import Path
                import os
                
                cache_dir = Path(os.path.expanduser("~/.cache/huggingface/hub"))
                if cache_dir.exists():
                    cache_contents = str(list(cache_dir.iterdir()))
                    status["sentiment"] = "bert-base-multilingual-uncased-sentiment" in cache_contents
                    status["embeddings"] = "all-MiniLM-L6-v2" in cache_contents
            except Exception:
                pass
            
            # Check for bundled models in models/ directory
            models_dir = Path(__file__).parent / "models"
            status["subjectivity"] = (models_dir / "subjectivity_task").exists()
            status["categories"] = (models_dir / "multilabel_task").exists()
            
            # Also check in parent's models directory (for pipeline structure)
            if not status["subjectivity"]:
                alt_models_dir = Path(__file__).parent.parent / "models"
                status["subjectivity"] = (alt_models_dir / "subjectivity_task").exists()
                status["categories"] = (alt_models_dir / "multilabel_task").exists()
            
        except Exception as e:
            print(json.dumps({
                "type": "error",
                "message": f"Error checking models: {str(e)}"
            }), flush=True)
        
        return {"success": True, "status": status}
    
    def _download_models(self, command: Dict) -> Dict:
        """Download required HuggingFace models with progress tracking."""
        results = {
            "sentiment": False,
            "embeddings": False,
            "subjectivity": True,  # Bundled models assumed present
            "categories": True,
        }
        
        models_to_download = [
            ("sentiment", "nlptown/bert-base-multilingual-uncased-sentiment", "transformers"),
            ("embeddings", "sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers"),
        ]
        
        for key, model_name, model_type in models_to_download:
            try:
                # Report start
                print(json.dumps({
                    "type": "progress",
                    "subtype": "model_download",
                    "model": key,
                    "progress": 0,
                    "message": f"Downloading {model_name}..."
                }), flush=True)
                
                # Download model
                if model_type == "transformers":
                    try:
                        from transformers import AutoTokenizer, AutoModelForSequenceClassification
                        AutoTokenizer.from_pretrained(model_name)
                        AutoModelForSequenceClassification.from_pretrained(model_name)
                    except ImportError:
                        print(json.dumps({
                            "type": "progress",
                            "subtype": "model_download",
                            "model": key,
                            "progress": -1,
                            "error": "transformers package not installed"
                        }), flush=True)
                        continue
                        
                elif model_type == "sentence-transformers":
                    try:
                        from sentence_transformers import SentenceTransformer
                        SentenceTransformer(model_name)
                    except ImportError:
                        print(json.dumps({
                            "type": "progress",
                            "subtype": "model_download",
                            "model": key,
                            "progress": -1,
                            "error": "sentence-transformers package not installed"
                        }), flush=True)
                        continue
                
                # Report complete
                print(json.dumps({
                    "type": "progress",
                    "subtype": "model_download",
                    "model": key,
                    "progress": 100,
                    "message": f"{model_name} downloaded"
                }), flush=True)
                
                results[key] = True
                
            except Exception as e:
                results[key] = False
                print(json.dumps({
                    "type": "progress",
                    "subtype": "model_download",
                    "model": key,
                    "progress": -1,
                    "error": str(e)
                }), flush=True)
        
        # Check bundled models
        models_dir = Path(__file__).parent / "models"
        alt_models_dir = Path(__file__).parent.parent / "models"
        
        subj_exists = (models_dir / "subjectivity_task").exists() or (alt_models_dir / "subjectivity_task").exists()
        cat_exists = (models_dir / "multilabel_task").exists() or (alt_models_dir / "multilabel_task").exists()
        
        results["subjectivity"] = subj_exists
        results["categories"] = cat_exists
        
        # Report bundled model status
        for key, exists in [("subjectivity", subj_exists), ("categories", cat_exists)]:
            print(json.dumps({
                "type": "progress",
                "subtype": "model_download",
                "model": key,
                "progress": 100 if exists else -1,
                "message": f"{key} model {'found' if exists else 'not found'}"
            }), flush=True)
        
        return {"success": all(results.values()), "details": results}
    
    def _download_model(self, command: Dict) -> Dict:
        """Download a specific model."""
        model_key = command.get("model")
        
        model_map = {
            "sentiment": ("nlptown/bert-base-multilingual-uncased-sentiment", "transformers"),
            "embeddings": ("sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers"),
        }
        
        if model_key not in model_map:
            return {"success": False, "error": f"Unknown model: {model_key}"}
        
        model_name, model_type = model_map[model_key]
        
        try:
            if model_type == "transformers":
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                AutoTokenizer.from_pretrained(model_name)
                AutoModelForSequenceClassification.from_pretrained(model_name)
            elif model_type == "sentence-transformers":
                from sentence_transformers import SentenceTransformer
                SentenceTransformer(model_name)
            
            return {"success": True, "model": model_key}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_download_size(self, command: Dict) -> Dict:
        """Get total download size for models."""
        # Estimated sizes in MB
        sizes = {
            "sentiment": 420,
            "embeddings": 80,
            "subjectivity": 440,
            "categories": 440,
        }
        
        # Check what's already downloaded
        status_result = self._check_models_status({})
        status = status_result.get("status", {})
        
        total_size = sum(
            size for key, size in sizes.items() 
            if not status.get(key, False)
        )
        
        return {"success": True, "size_mb": total_size}


def main():
    """Main entry point for subprocess communication."""
    api = PipelineAPI()
    
    # Cleanup old backup sessions on startup
    if api.rollback_manager:
        cleaned = api.rollback_manager.cleanup_old_backups(max_age_hours=24)
        if cleaned > 0:
            print(json.dumps({
                "type": "info", 
                "message": f"Cleaned up {cleaned} old backup session(s)"
            }), flush=True)
    
    # Send ready signal
    print(json.dumps({"type": "ready", "status": "initialized"}), flush=True)
    
    # Read commands from stdin, write responses to stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            command = json.loads(line)
            result = api.execute(command)
            print(json.dumps(result), flush=True)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "success": False,
                "error": f"Invalid JSON: {e}"
            }), flush=True)


if __name__ == "__main__":
    main()
