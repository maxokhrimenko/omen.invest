"""
Logging decorators for easy integration across the application.

This module provides decorators for:
- Timing operations
- Logging function entry/exit
- Error handling with logging
- API call logging
- Business operation logging
"""

import time
import functools
from typing import Callable, Any, Optional, Dict
from .logger_service import get_logger_service


def log_operation(operation_name: str, include_args: bool = False, include_result: bool = False):
    """Decorator to log function entry, execution time, and exit."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger_service = get_logger_service()
            logger = logger_service.get_logger("business")
            
            # Log function entry
            log_details = {}
            if include_args:
                log_details["args"] = str(args)[:200]  # Limit length
                log_details["kwargs"] = str(kwargs)[:200]
            
            logger.debug(f"Starting {operation_name}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log success
                success_details = {"duration": f"{duration:.4f}s"}
                if include_result and result is not None:
                    success_details["result"] = str(result)[:200]
                
                logger.info(f"Completed {operation_name} successfully")
                logger_service.log_performance(operation_name, duration, success_details)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {operation_name} after {duration:.4f}s: {str(e)}")
                logger_service.log_business_operation(
                    operation_name, 
                    "ERROR", 
                    False, 
                    {"error": str(e), "duration": f"{duration:.4f}s"}
                )
                raise
        return wrapper
    return decorator


def log_api_call(api_name: str, include_request: bool = False, include_response: bool = False):
    """Decorator to log API calls with timing and status."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger_service = get_logger_service()
            logger = logger_service.get_logger("api")
            
            # Extract endpoint from function name or args
            endpoint = func.__name__
            if args and hasattr(args[0], 'symbol'):
                endpoint = f"{endpoint}/{args[0].symbol}"
            
            # Log API call start
            call_details = {}
            if include_request:
                call_details["request"] = str(args)[:200]
            
            logger.debug(f"API call started: {api_name} - {endpoint}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log success
                success_details = {"duration": f"{duration:.4f}s", "status": "SUCCESS"}
                if include_response and result is not None:
                    success_details["response"] = str(result)[:200]
                
                logger.info(f"API call successful: {api_name} - {endpoint}")
                logger_service.log_api_call(api_name, endpoint, "CALL", duration, "SUCCESS", success_details)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"API call failed: {api_name} - {endpoint}: {str(e)}")
                logger_service.log_api_call(
                    api_name, 
                    endpoint, 
                    "CALL", 
                    duration, 
                    "ERROR", 
                    {"error": str(e)}
                )
                raise
        return wrapper
    return decorator


def log_file_operation(operation_type: str, include_path: bool = True):
    """Decorator to log file operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger_service = get_logger_service()
            logger = logger_service.get_logger("file")
            
            # Extract file path from args
            file_path = "unknown"
            if include_path and args:
                file_path = str(args[0]) if len(args) > 0 else "unknown"
            
            logger.debug(f"File operation started: {operation_type} - {file_path}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log success
                success_details = {"duration": f"{duration:.4f}s"}
                if include_path:
                    success_details["file_path"] = file_path
                
                logger.info(f"File operation successful: {operation_type} - {file_path}")
                logger_service.log_file_operation(operation_type, file_path, True, success_details)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"File operation failed: {operation_type} - {file_path}: {str(e)}")
                logger_service.log_file_operation(
                    operation_type, 
                    file_path, 
                    False, 
                    {"error": str(e), "duration": f"{duration:.4f}s"}
                )
                raise
        return wrapper
    return decorator


def log_user_action(action_name: str, include_inputs: bool = True):
    """Decorator to log user actions and inputs."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger_service = get_logger_service()
            logger = logger_service.get_logger("user")
            
            # Log user action
            action_details = {}
            if include_inputs:
                action_details["args"] = str(args)[:200]
                action_details["kwargs"] = str(kwargs)[:200]
            
            logger.info(f"User action: {action_name}")
            logger_service.log_user_action(action_name, action_details)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log success
                success_details = {"duration": f"{duration:.4f}s"}
                logger.info(f"User action completed: {action_name}")
                logger_service.log_user_action(f"{action_name}_completed", success_details)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"User action failed: {action_name}: {str(e)}")
                logger_service.log_user_action(
                    f"{action_name}_failed", 
                    {"error": str(e), "duration": f"{duration:.4f}s"}
                )
                raise
        return wrapper
    return decorator


def log_validation(validation_type: str):
    """Decorator to log validation operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger_service = get_logger_service()
            logger = logger_service.get_logger("validation")
            
            logger.debug(f"Validation started: {validation_type}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.debug(f"Validation successful: {validation_type}")
                logger_service.log_business_operation(
                    f"validate_{validation_type}", 
                    "validation", 
                    True, 
                    {"duration": f"{duration:.4f}s"}
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.warning(f"Validation failed: {validation_type}: {str(e)}")
                logger_service.log_business_operation(
                    f"validate_{validation_type}", 
                    "validation", 
                    False, 
                    {"error": str(e), "duration": f"{duration:.4f}s"}
                )
                raise
        return wrapper
    return decorator


def log_calculation(calculation_type: str, include_inputs: bool = False, include_outputs: bool = False):
    """Decorator to log calculation operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger_service = get_logger_service()
            logger = logger_service.get_logger("calculation")
            
            # Log calculation start
            calc_details = {}
            if include_inputs:
                calc_details["inputs"] = str(args)[:200]
            
            logger.debug(f"Calculation started: {calculation_type}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log success
                success_details = {"duration": f"{duration:.4f}s"}
                if include_outputs and result is not None:
                    success_details["outputs"] = str(result)[:200]
                
                logger.debug(f"Calculation completed: {calculation_type}")
                logger_service.log_business_operation(
                    f"calculate_{calculation_type}", 
                    "calculation", 
                    True, 
                    success_details
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Calculation failed: {calculation_type}: {str(e)}")
                logger_service.log_business_operation(
                    f"calculate_{calculation_type}", 
                    "calculation", 
                    False, 
                    {"error": str(e), "duration": f"{duration:.4f}s"}
                )
                raise
        return wrapper
    return decorator
