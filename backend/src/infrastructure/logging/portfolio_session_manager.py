"""
Portfolio Session Manager - Manages frontend logging by portfolio sessions.

This module provides:
- Portfolio session tracking with UUIDs
- Centralized logging per portfolio session
- Session lifecycle management
- Portfolio-based log file organization
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class PortfolioSessionManager:
    """Manages portfolio sessions and their associated logging."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.frontend_logs_dir = self.logs_dir / "frontend"
        self.backend_logs_dir = self.logs_dir / "backend"
        self.frontend_logs_dir.mkdir(parents=True, exist_ok=True)
        self.backend_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Active portfolio sessions: {portfolio_uuid: session_info}
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._loggers: Dict[str, logging.Logger] = {}
        self._backend_loggers: Dict[str, logging.Logger] = {}
    
    def start_portfolio_session(self, portfolio_name: str = None) -> str:
        """Start a new portfolio session and return its UUID."""
        portfolio_uuid = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Create session info
        session_info = {
            "uuid": portfolio_uuid,
            "name": portfolio_name or f"portfolio-{timestamp}",
            "start_time": datetime.now(),
            "frontend_log_file": self.frontend_logs_dir / f"portfolio-{portfolio_uuid}-{timestamp}.log",
            "backend_log_file": self.backend_logs_dir / f"portfolio-{portfolio_uuid}-{timestamp}.log"
        }
        
        # Create frontend logger for this portfolio session
        frontend_logger = self._create_portfolio_logger(portfolio_uuid, session_info["frontend_log_file"])
        
        # Create backend logger for this portfolio session
        backend_logger = self._create_backend_portfolio_logger(portfolio_uuid, session_info["backend_log_file"])
        
        # Store session info
        self._active_sessions[portfolio_uuid] = session_info
        self._loggers[portfolio_uuid] = frontend_logger
        self._backend_loggers[portfolio_uuid] = backend_logger
        
        # Log session start to frontend log
        frontend_logger.info(f"=== PORTFOLIO SESSION STARTED ===")
        frontend_logger.info(f"Portfolio UUID: {portfolio_uuid}")
        frontend_logger.info(f"Portfolio Name: {session_info['name']}")
        frontend_logger.info(f"Session Start: {session_info['start_time']}")
        frontend_logger.info(f"Log File: {session_info['frontend_log_file']}")
        frontend_logger.info("=" * 50)
        
        # Log session start to backend log
        backend_logger.info(f"=== PORTFOLIO SESSION STARTED ===")
        backend_logger.info(f"Portfolio UUID: {portfolio_uuid}")
        backend_logger.info(f"Portfolio Name: {session_info['name']}")
        backend_logger.info(f"Session Start: {session_info['start_time']}")
        backend_logger.info(f"Log File: {session_info['backend_log_file']}")
        backend_logger.info("=" * 50)
        
        return portfolio_uuid
    
    def get_portfolio_logger(self, portfolio_uuid: str) -> Optional[logging.Logger]:
        """Get frontend logger for a specific portfolio session."""
        return self._loggers.get(portfolio_uuid)
    
    def get_backend_portfolio_logger(self, portfolio_uuid: str) -> Optional[logging.Logger]:
        """Get backend logger for a specific portfolio session."""
        return self._backend_loggers.get(portfolio_uuid)
    
    def log_portfolio_operation(self, portfolio_uuid: str, operation: str, 
                               success: bool, details: Optional[Dict[str, Any]] = None):
        """Log a portfolio operation to both frontend and backend logs."""
        frontend_logger = self.get_portfolio_logger(portfolio_uuid)
        backend_logger = self.get_backend_portfolio_logger(portfolio_uuid)
        
        status = "SUCCESS" if success else "FAILED"
        message = f"OP | {operation} | {status}"
        
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        
        if frontend_logger:
            frontend_logger.info(message)
        if backend_logger:
            backend_logger.info(message)
    
    def log_portfolio_error(self, portfolio_uuid: str, error: str, 
                           operation: str = None, details: Optional[Dict[str, Any]] = None):
        """Log a portfolio error to both frontend and backend logs."""
        frontend_logger = self.get_portfolio_logger(portfolio_uuid)
        backend_logger = self.get_backend_portfolio_logger(portfolio_uuid)
        
        message = f"ERR | {error}"
        if operation:
            message += f" | Operation: {operation}"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        
        if frontend_logger:
            frontend_logger.error(message)
        if backend_logger:
            backend_logger.error(message)
    
    def log_portfolio_request(self, portfolio_uuid: str, method: str, endpoint: str,
                             duration: Optional[float] = None, status: Optional[str] = None,
                             details: Optional[Dict[str, Any]] = None):
        """Log a portfolio-related API request to both frontend and backend logs."""
        frontend_logger = self.get_portfolio_logger(portfolio_uuid)
        backend_logger = self.get_backend_portfolio_logger(portfolio_uuid)
        
        message = f"REQ | {method} {endpoint}"
        if status:
            message += f" | Status: {status}"
        if duration:
            message += f" | Duration: {duration:.4f}s"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" | {detail_str}"
        
        if frontend_logger:
            frontend_logger.info(message)
        if backend_logger:
            backend_logger.info(message)
    
    def end_portfolio_session(self, portfolio_uuid: str, reason: str = "completed"):
        """End a portfolio session."""
        if portfolio_uuid not in self._active_sessions:
            return
        
        session_info = self._active_sessions[portfolio_uuid]
        frontend_logger = self._loggers.get(portfolio_uuid)
        backend_logger = self._backend_loggers.get(portfolio_uuid)
        
        session_duration = datetime.now() - session_info["start_time"]
        end_message = "=" * 50
        end_message += f"\n=== PORTFOLIO SESSION ENDED ==="
        end_message += f"\nPortfolio UUID: {portfolio_uuid}"
        end_message += f"\nSession Duration: {session_duration}"
        end_message += f"\nEnd Reason: {reason}"
        end_message += f"\nSession End: {datetime.now()}"
        end_message += f"\n" + "=" * 50
        
        if frontend_logger:
            frontend_logger.info(end_message)
        if backend_logger:
            backend_logger.info(end_message)
        
        # Clean up
        del self._active_sessions[portfolio_uuid]
        if portfolio_uuid in self._loggers:
            del self._loggers[portfolio_uuid]
        if portfolio_uuid in self._backend_loggers:
            del self._backend_loggers[portfolio_uuid]
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active portfolio sessions."""
        return self._active_sessions.copy()
    
    def _create_portfolio_logger(self, portfolio_uuid: str, log_file: Path) -> logging.Logger:
        """Create a frontend logger for a specific portfolio session."""
        logger_name = f"portfolio-{portfolio_uuid}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s:%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger
    
    def _create_backend_portfolio_logger(self, portfolio_uuid: str, log_file: Path) -> logging.Logger:
        """Create a backend logger for a specific portfolio session."""
        logger_name = f"backend-portfolio-{portfolio_uuid}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s:%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger


# Global portfolio session manager instance
_portfolio_session_manager: Optional[PortfolioSessionManager] = None


def get_portfolio_session_manager() -> PortfolioSessionManager:
    """Get the global portfolio session manager instance."""
    global _portfolio_session_manager
    if _portfolio_session_manager is None:
        # Use absolute path to project root logs directory
        import os
        # Get the project root directory (5 levels up from this file)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        logs_dir = os.path.join(project_root, "logs")
        _portfolio_session_manager = PortfolioSessionManager(logs_dir)
    return _portfolio_session_manager


def initialize_portfolio_session_manager(logs_dir: str = "logs") -> PortfolioSessionManager:
    """Initialize the global portfolio session manager."""
    global _portfolio_session_manager
    _portfolio_session_manager = PortfolioSessionManager(logs_dir)
    return _portfolio_session_manager
