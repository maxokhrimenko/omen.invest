"""
LoggerService - Centralized logging service for the Portfolio Analysis Tool.

This service provides:
- Session-based log separation
- Human-readable log format
- File-based logging with rotation
- Performance timing
- Comprehensive error logging
"""

import os
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager
from functools import wraps


class LoggerService:
    """Centralized logging service with session management."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        self.session_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_directories()
        self._setup_logging()
    
    def _setup_directories(self):
        """Create necessary log directories."""
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(os.path.join(self.logs_dir, "sessions"), exist_ok=True)
        os.makedirs(os.path.join(self.logs_dir, "frontend"), exist_ok=True)
        os.makedirs(os.path.join(self.logs_dir, "total"), exist_ok=True)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Configure root logger with minimal console output and file logging
        logging.basicConfig(
            level=logging.INFO,  # Allow INFO and above for console
            format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[]  # No handlers for root logger
        )
    
    def start_session(self) -> str:
        """Start a new logging session."""
        self.session_id = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.session_start_time = datetime.now()
        
        # Create session-specific logger
        session_logger = self._create_logger(
            name="session",
            log_file=os.path.join(self.logs_dir, "sessions", f"session-{self.session_id}.log")
        )
        
        # Log session start
        session_logger.info(f"=== SESSION STARTED: {self.session_id} ===")
        session_logger.info(f"Session started at: {self.session_start_time}")
        
        return self.session_id
    
    def end_session(self):
        """End the current logging session."""
        if self.session_id and self.session_start_time:
            session_duration = datetime.now() - self.session_start_time
            session_logger = self.get_logger("session")
            session_logger.info(f"Session duration: {session_duration}")
            session_logger.info(f"=== SESSION ENDED: {self.session_id} ===")
            
            # Log to total logs as well
            total_logger = self.get_logger("total")
            total_logger.info(f"Session {self.session_id} ended after {session_duration}")
            
            self.session_id = None
            self.session_start_time = None
    
    def start_frontend_session(self, request_id: str = None) -> str:
        """Start a new frontend logging session based on request ID."""
        if not request_id:
            request_id = f"req-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:-3]}"
        
        # Create frontend session-specific logger
        frontend_logger = self._create_logger(
            name="frontend",
            log_file=os.path.join(self.logs_dir, "frontend", f"frontend-{request_id}.log")
        )
        
        # Log frontend session start
        frontend_logger.info(f"=== FRONTEND SESSION STARTED: {request_id} ===")
        frontend_logger.info(f"Frontend session started at: {datetime.now()}")
        
        return request_id
    
    def get_frontend_logger(self, request_id: str) -> logging.Logger:
        """Get a logger for a specific frontend request session."""
        logger_name = f"frontend-{request_id}"
        
        if logger_name not in self._loggers:
            # Create frontend session logger
            self._loggers[logger_name] = self._create_logger(
                name=logger_name,
                log_file=os.path.join(self.logs_dir, "frontend", f"frontend-{request_id}.log")
            )
        else:
            # If we have an active frontend session, ensure it has a frontend handler
            if not any(isinstance(h, logging.FileHandler) and 
                      f"frontend-{request_id}.log" in h.baseFilename 
                      for h in self._loggers[logger_name].handlers):
                frontend_log_file = os.path.join(self.logs_dir, "frontend", f"frontend-{request_id}.log")
                frontend_handler = logging.FileHandler(frontend_log_file, mode='a', encoding='utf-8')
                frontend_handler.setLevel(logging.DEBUG)
                frontend_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s:%(lineno)-4d | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                frontend_handler.setFormatter(frontend_formatter)
                self._loggers[logger_name].addHandler(frontend_handler)
        
        return self._loggers[logger_name]
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger for the given name."""
        if name not in self._loggers:
            self._loggers[name] = self._create_logger(name)
        else:
            # If we have an active session and this logger doesn't have a session handler,
            # add one to it
            if (self.session_id and name != "session" and 
                not any(isinstance(h, logging.FileHandler) and 
                       f"session-{self.session_id}.log" in h.baseFilename 
                       for h in self._loggers[name].handlers)):
                session_log_file = os.path.join(self.logs_dir, "sessions", f"session-{self.session_id}.log")
                session_handler = logging.FileHandler(session_log_file, mode='a', encoding='utf-8')
                session_handler.setLevel(logging.DEBUG)
                session_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s:%(lineno)-4d | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                session_handler.setFormatter(session_formatter)
                self._loggers[name].addHandler(session_handler)
        return self._loggers[name]
    
    def _create_logger(self, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """Create a logger with both console and file handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Generate unique log ID for this logger instance
        import uuid
        log_id = str(uuid.uuid4())[:8]
        
        # Console handler with minimal output and log ID
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            f'[%(levelname)s] %(message)s (ID: {log_id})',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler for total logs
        if log_file:
            # This is a specific log file (like session logs)
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        else:
            # Default to total logs
            file_handler = logging.FileHandler(
                os.path.join(self.logs_dir, "total", "application.log"),
                mode='a',
                encoding='utf-8'
            )
        
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            f'%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s:%(lineno)-4d | LOG_ID:{log_id} | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # If this is not the session logger and we have an active session, 
        # also add a handler to the session log file
        if name != "session" and self.session_id and not log_file:
            session_log_file = os.path.join(self.logs_dir, "sessions", f"session-{self.session_id}.log")
            session_handler = logging.FileHandler(session_log_file, mode='a', encoding='utf-8')
            session_handler.setLevel(logging.DEBUG)
            session_handler.setFormatter(file_formatter)
            logger.addHandler(session_handler)
        
        # Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False
        
        return logger
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """Log performance metrics for an operation."""
        logger = self.get_logger("performance")
        message = f"PERF | {operation} | Duration: {duration:.4f}s"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        logger.info(message)
    
    def log_user_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Log user actions and inputs."""
        logger = self.get_logger("user")
        message = f"USER | {action}"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        logger.info(message)
    
    def log_api_call(self, api_name: str, endpoint: str, method: str, 
                    duration: Optional[float] = None, status: Optional[str] = None,
                    details: Optional[Dict[str, Any]] = None):
        """Log external API calls."""
        logger = self.get_logger("api")
        message = f"API | {api_name} | {method} {endpoint}"
        if status:
            message += f" | Status: {status}"
        if duration:
            message += f" | Duration: {duration:.4f}s"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        logger.info(message)
    
    def log_file_operation(self, operation: str, file_path: str, 
                          success: bool, details: Optional[Dict[str, Any]] = None):
        """Log file operations."""
        logger = self.get_logger("file")
        status = "SUCCESS" if success else "FAILED"
        message = f"FILE | {operation} | {file_path} | {status}"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        logger.info(message)
    
    def log_business_operation(self, operation: str, layer: str, 
                              success: bool, details: Optional[Dict[str, Any]] = None):
        """Log business operations."""
        logger = self.get_logger("business")
        status = "SUCCESS" if success else "FAILED"
        message = f"BIZ | {layer} | {operation} | {status}"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        logger.info(message)
    
    def log_frontend_request(self, request_id: str, method: str, endpoint: str, 
                           duration: Optional[float] = None, status: Optional[str] = None,
                           details: Optional[Dict[str, Any]] = None):
        """Log frontend API requests."""
        logger = self.get_frontend_logger(request_id)
        message = f"REQ | {method} {endpoint}"
        if status:
            message += f" | Status: {status}"
        if duration:
            message += f" | Duration: {duration:.4f}s"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        logger.info(message)
    
    def log_frontend_error(self, request_id: str, error: str, endpoint: str = None, 
                          details: Optional[Dict[str, Any]] = None):
        """Log frontend errors."""
        logger = self.get_frontend_logger(request_id)
        message = f"ERR | {error}"
        if endpoint:
            message += f" | Endpoint: {endpoint}"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        logger.error(message)
    
    def log_frontend_operation(self, request_id: str, operation: str, 
                              success: bool, details: Optional[Dict[str, Any]] = None):
        """Log frontend operations."""
        logger = self.get_frontend_logger(request_id)
        status = "SUCCESS" if success else "FAILED"
        message = f"OP | {operation} | {status}"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        logger.info(message)
    
    @contextmanager
    def time_operation(self, operation_name: str, details: Optional[Dict[str, Any]] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        logger = self.get_logger("performance")
        logger.debug(f"Starting operation: {operation_name}")
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.log_performance(operation_name, duration, details)
    
    def timing_decorator(self, operation_name: str, include_args: bool = False):
        """Decorator for timing function execution."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                logger = self.get_logger("performance")
                
                # Log function start
                log_details = {}
                if include_args:
                    log_details["args"] = str(args)[:100]  # Limit length
                    log_details["kwargs"] = str(kwargs)[:100]
                
                logger.debug(f"Starting {operation_name}")
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.log_performance(operation_name, duration, log_details)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(f"Operation {operation_name} failed after {duration:.4f}s: {str(e)}")
                    raise
            return wrapper
        return decorator


# Global logger service instance
_logger_service: Optional[LoggerService] = None


def get_logger_service() -> LoggerService:
    """Get the global logger service instance."""
    global _logger_service
    if _logger_service is None:
        _logger_service = LoggerService()
    return _logger_service


def initialize_logging(logs_dir: str = "logs") -> LoggerService:
    """Initialize the global logger service."""
    global _logger_service
    _logger_service = LoggerService(logs_dir)
    return _logger_service


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return get_logger_service().get_logger(name)
