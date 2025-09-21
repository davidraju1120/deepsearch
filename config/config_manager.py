import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict, field
from dotenv import load_dotenv

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: str = "all-MiniLM-L6-v2"
    device: str = "cpu"
    batch_size: int = 32
    max_length: int = 512
    cache_dir: Optional[str] = None
    use_cache: bool = True

@dataclass
class StorageConfig:
    """Configuration for document storage."""
    data_dir: str = "data"
    documents_dir: str = "documents"
    embeddings_dir: str = "embeddings"
    indexes_dir: str = "indexes"
    max_documents: int = 10000
    chunk_size: int = 1000
    chunk_overlap: int = 200

@dataclass
class ReasoningConfig:
    """Configuration for reasoning engine."""
    max_steps: int = 10
    confidence_threshold: float = 0.5
    enable_multi_step: bool = True
    enable_explanation: bool = True
    reasoning_timeout: int = 300

@dataclass
class QueryConfig:
    """Configuration for query handling."""
    max_results: int = 10
    similarity_threshold: float = 0.7
    enable_refinement: bool = True
    max_refinement_rounds: int = 3
    enable_summarization: bool = True
    summary_type: str = "hybrid"

@dataclass
class ProcessingConfig:
    """Configuration for document processing."""
    supported_formats: List[str] = field(default_factory=lambda: [".txt", ".md", ".pdf", ".docx", ".html", ".json"])
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    chunk_size: int = 1000
    chunk_overlap: int = 200
    clean_text: bool = True
    extract_metadata: bool = True

@dataclass
class ExportConfig:
    """Configuration for export functionality."""
    output_dir: str = "exports"
    default_format: str = "pdf"
    supported_formats: List[str] = field(default_factory=lambda: ["pdf", "markdown", "json"])
    include_metadata: bool = True
    include_reasoning: bool = True

@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class AppConfig:
    """Main application configuration."""
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    reasoning: ReasoningConfig = field(default_factory=ReasoningConfig)
    query: QueryConfig = field(default_factory=QueryConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # General settings
    debug: bool = False
    version: str = "1.0.0"
    data_dir: str = "data"
    config_file: Optional[str] = None

class ConfigManager:
    """
    Configuration manager for the Deep Researcher Agent.
    Handles loading, saving, and managing configuration settings.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file = config_file or "config/config.json"
        self.config_dir = Path(self.config_file).parent
        self.config_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize default configuration
        self.config = AppConfig()
        
        # Load configuration from file if it exists
        self.load_config()
        
        # Setup logging
        self.setup_logging()
        
        logging.info(f"ConfigManager initialized with config file: {self.config_file}")
    
    def load_config(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update configuration with loaded data
                self._update_config_from_dict(config_data)
                logging.info(f"Configuration loaded from {self.config_file}")
                return True
            else:
                logging.info(f"Configuration file not found: {self.config_file}. Using defaults.")
                return False
                
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            config_dict = asdict(self.config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
            return False
    
    def get_config(self) -> AppConfig:
        """
        Get the current configuration.
        
        Returns:
            Current AppConfig instance
        """
        return self.config
    
    def get_embedding_config(self) -> EmbeddingConfig:
        """Get embedding configuration."""
        return self.config.embedding
    
    def get_storage_config(self) -> StorageConfig:
        """Get storage configuration."""
        return self.config.storage
    
    def get_reasoning_config(self) -> ReasoningConfig:
        """Get reasoning configuration."""
        return self.config.reasoning
    
    def get_query_config(self) -> QueryConfig:
        """Get query configuration."""
        return self.config.query
    
    def get_processing_config(self) -> ProcessingConfig:
        """Get processing configuration."""
        return self.config.processing
    
    def get_export_config(self) -> ExportConfig:
        """Get export configuration."""
        return self.config.export
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return self.config.logging
    
    def update_config(self, config_dict: Dict[str, Any]) -> bool:
        """
        Update configuration with provided dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._update_config_from_dict(config_dict)
            logging.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error updating configuration: {e}")
            return False
    
    def update_embedding_config(self, **kwargs) -> bool:
        """
        Update embedding configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.embedding, key):
                    setattr(self.config.embedding, key, value)
                else:
                    logging.warning(f"Unknown embedding config parameter: {key}")
            
            logging.info("Embedding configuration updated")
            return True
            
        except Exception as e:
            logging.error(f"Error updating embedding configuration: {e}")
            return False
    
    def update_storage_config(self, **kwargs) -> bool:
        """
        Update storage configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.storage, key):
                    setattr(self.config.storage, key, value)
                else:
                    logging.warning(f"Unknown storage config parameter: {key}")
            
            logging.info("Storage configuration updated")
            return True
            
        except Exception as e:
            logging.error(f"Error updating storage configuration: {e}")
            return False
    
    def update_reasoning_config(self, **kwargs) -> bool:
        """
        Update reasoning configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.reasoning, key):
                    setattr(self.config.reasoning, key, value)
                else:
                    logging.warning(f"Unknown reasoning config parameter: {key}")
            
            logging.info("Reasoning configuration updated")
            return True
            
        except Exception as e:
            logging.error(f"Error updating reasoning configuration: {e}")
            return False
    
    def update_query_config(self, **kwargs) -> bool:
        """
        Update query configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.query, key):
                    setattr(self.config.query, key, value)
                else:
                    logging.warning(f"Unknown query config parameter: {key}")
            
            logging.info("Query configuration updated")
            return True
            
        except Exception as e:
            logging.error(f"Error updating query configuration: {e}")
            return False
    
    def update_processing_config(self, **kwargs) -> bool:
        """
        Update processing configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.processing, key):
                    setattr(self.config.processing, key, value)
                else:
                    logging.warning(f"Unknown processing config parameter: {key}")
            
            logging.info("Processing configuration updated")
            return True
            
        except Exception as e:
            logging.error(f"Error updating processing configuration: {e}")
            return False
    
    def update_export_config(self, **kwargs) -> bool:
        """
        Update export configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.export, key):
                    setattr(self.config.export, key, value)
                else:
                    logging.warning(f"Unknown export config parameter: {key}")
            
            logging.info("Export configuration updated")
            return True
            
        except Exception as e:
            logging.error(f"Error updating export configuration: {e}")
            return False
    
    def update_logging_config(self, **kwargs) -> bool:
        """
        Update logging configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.logging, key):
                    setattr(self.config.logging, key, value)
                else:
                    logging.warning(f"Unknown logging config parameter: {key}")
            
            logging.info("Logging configuration updated")
            return True
            
        except Exception as e:
            logging.error(f"Error updating logging configuration: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config = AppConfig()
            logging.info("Configuration reset to defaults")
            return True
            
        except Exception as e:
            logging.error(f"Error resetting configuration: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """
        Validate current configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate embedding config
        if self.config.embedding.batch_size <= 0:
            errors.append("Embedding batch_size must be positive")
        
        if self.config.embedding.max_length <= 0:
            errors.append("Embedding max_length must be positive")
        
        # Validate storage config
        if self.config.storage.max_documents <= 0:
            errors.append("Storage max_documents must be positive")
        
        if self.config.storage.chunk_size <= 0:
            errors.append("Storage chunk_size must be positive")
        
        # Validate reasoning config
        if self.config.reasoning.max_steps <= 0:
            errors.append("Reasoning max_steps must be positive")
        
        if not 0 <= self.config.reasoning.confidence_threshold <= 1:
            errors.append("Reasoning confidence_threshold must be between 0 and 1")
        
        # Validate query config
        if self.config.query.max_results <= 0:
            errors.append("Query max_results must be positive")
        
        if not 0 <= self.config.query.similarity_threshold <= 1:
            errors.append("Query similarity_threshold must be between 0 and 1")
        
        # Validate processing config
        if self.config.processing.max_file_size <= 0:
            errors.append("Processing max_file_size must be positive")
        
        if self.config.processing.chunk_size <= 0:
            errors.append("Processing chunk_size must be positive")
        
        # Validate export config
        if self.config.export.default_format not in self.config.export.supported_formats:
            errors.append("Export default_format must be one of supported formats")
        
        # Validate logging config
        if self.config.logging.level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append("Logging level must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL")
        
        return errors
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current configuration.
        
        Returns:
            Configuration summary dictionary
        """
        return {
            "config_file": self.config_file,
            "embedding_model": self.config.embedding.model_name,
            "embedding_device": self.config.embedding.device,
            "data_directory": self.config.storage.data_dir,
            "max_documents": self.config.storage.max_documents,
            "reasoning_enabled": self.config.reasoning.enable_multi_step,
            "explanation_enabled": self.config.reasoning.enable_explanation,
            "query_refinement_enabled": self.config.query.enable_refinement,
            "summarization_enabled": self.config.query.enable_summarization,
            "export_formats": self.config.export.supported_formats,
            "debug_mode": self.config.debug,
            "version": self.config.version
        }
    
    def setup_logging(self):
        """Setup logging based on configuration."""
        try:
            log_config = self.config.logging
            
            # Configure logging level
            level = getattr(logging, log_config.level.upper(), logging.INFO)
            
            # Configure logging format
            formatter = logging.Formatter(log_config.format)
            
            # Setup root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(level)
            
            # Clear existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Add console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
            
            # Add file handler if specified
            if log_config.file_path:
                # Create log directory if it doesn't exist
                log_file = Path(log_config.file_path)
                log_file.parent.mkdir(parents=True, exist_ok=True)
                
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    log_config.file_path,
                    maxBytes=log_config.max_file_size,
                    backupCount=log_config.backup_count
                )
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            
            logging.info("Logging setup completed")
            
        except Exception as e:
            logging.error(f"Error setting up logging: {e}")
    
    def _update_config_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary."""
        # Update main config
        for key, value in config_dict.items():
            if hasattr(self.config, key):
                if key in ["embedding", "storage", "reasoning", "query", "processing", "export", "logging"]:
                    # Handle nested configurations
                    nested_config = getattr(self.config, key)
                    if isinstance(value, dict):
                        for nested_key, nested_value in value.items():
                            if hasattr(nested_config, nested_key):
                                setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(self.config, key, value)
    
    def create_default_config_file(self) -> bool:
        """
        Create a default configuration file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Reset to defaults
            self.config = AppConfig()
            
            # Save to file
            return self.save_config()
            
        except Exception as e:
            logging.error(f"Error creating default config file: {e}")
            return False
    
    def get_environment_override(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value from environment variable with fallback.
        
        Args:
            key: Environment variable key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        env_key = f"DEEP_RESEARCHER_{key.upper()}"
        return os.getenv(env_key, default)
