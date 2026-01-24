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
from typing import Dict, Any, Optional
from pathlib import Path
from contextlib import contextmanager

# Track if full pipeline is available
PIPELINE_AVAILABLE = False
PIPELINE_ERROR = None

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

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
    
    def report(self, progress: int, message: str = ""):
        """Send progress update to Electron."""
        response = {
            "type": "progress",
            "phase": self.phase,
            "phaseName": self.phase_name,
            "progress": progress,
            "message": message
        }
        print(json.dumps(response), flush=True)


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
                "get_status": self._get_status,
                "validate_dataset": self._validate_dataset,
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
        """Run a specific pipeline phase."""
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
        reporter.report(0, "Iniciando fase...")
        
        try:
            # Redirect stdout to stderr to prevent pipeline print statements
            # from breaking JSON communication
            with redirect_stdout_to_stderr():
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
            
            reporter.report(100, "Fase completada")
            
            return {
                "success": True,
                "phase": phase,
                "phaseName": phase_name,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "phase": phase,
                "phaseName": phase_name,
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
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
        """Stop the current execution."""
        self.should_stop = True
        return {"success": True, "message": "Stop signal sent"}
    
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
            required_original = ["Titulo", "Review", "FechaEstadia", "Calificacion"]
            required_processed = ["TituloReview", "FechaEstadia", "Calificacion"]
            
            has_titulo_review = "TituloReview" in df.columns
            
            if has_titulo_review:
                required = required_processed
            else:
                required = required_original
            
            missing = [col for col in required if col not in df.columns]
            
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
