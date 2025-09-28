/**
 * Logging service for frontend
 * Provides logging format and correlation with backend
 */

export const LogLevel = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  CRITICAL: 4
} as const;

export type LogLevelType = typeof LogLevel[keyof typeof LogLevel];

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  context?: Record<string, unknown>;
  userId?: string;
  operation?: string;
  duration?: number;
  error?: {
    name: string;
    message: string;
    stack?: string;
  };
  logId?: string; // Unique ID for linking terminal output to log files
}

class Logger {
  private correlationId: string;
  private logLevel: LogLevelType;
  private enableConsole: boolean;
  private enableRemote: boolean;

  constructor() {
    this.correlationId = this.generateCorrelationId();
    this.logLevel = this.getLogLevel();
    this.enableConsole = import.meta.env.DEV;
    this.enableRemote = true;
  }


  private generateCorrelationId(): string {
    return `corr_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateLogId(): string {
    return `log_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
  }

  private getLogLevel(): LogLevelType {
    const level = import.meta.env.VITE_LOG_LEVEL || 'INFO';
    return LogLevel[level as keyof typeof LogLevel] || LogLevel.INFO;
  }

  private shouldLog(level: LogLevelType): boolean {
    return level >= this.logLevel;
  }

  private createLogEntry(
    level: string,
    message: string,
    context?: Record<string, unknown>,
    error?: Error
  ): LogEntry {
    const logId = this.generateLogId();
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      logId,
      context
    };

    if (error) {
      entry.error = {
        name: error.name,
        message: error.message,
        stack: error.stack
      };
    }

    return entry;
  }

  private formatTerminalOutput(entry: LogEntry): string {
    // Minimal terminal output with logId for linking to files
    return `[${entry.level}] ${entry.message} (ID: ${entry.logId})`;
  }

  private async sendToBackend(entry: LogEntry): Promise<void> {
    if (!this.enableRemote) return;

    try {
      await fetch('/api/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entry)
      });
    } catch (error) {
      // Silently fail to avoid infinite logging loops
      console.warn('Failed to send log to backend:', error);
    }
  }

  private log(level: LogLevelType, levelName: string, message: string, context?: Record<string, unknown>, error?: Error): void {
    if (!this.shouldLog(level)) return;

    const entry = this.createLogEntry(levelName, message, context, error);

    // Minimal console output with logId for linking
    if (this.enableConsole) {
      const terminalOutput = this.formatTerminalOutput(entry);
      const consoleMethod = level === LogLevel.ERROR || level === LogLevel.CRITICAL ? 'error' : 'log';
      console[consoleMethod](terminalOutput);
    }

    // Send to backend for file storage
    this.sendToBackend(entry);
  }

  debug(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.DEBUG, 'DEBUG', message, context);
  }

  info(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.INFO, 'INFO', message, context);
  }

  warn(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.WARN, 'WARN', message, context);
  }

  error(message: string, error?: Error, context?: Record<string, unknown>): void {
    this.log(LogLevel.ERROR, 'ERROR', message, context, error);
  }

  critical(message: string, error?: Error, context?: Record<string, unknown>): void {
    this.log(LogLevel.CRITICAL, 'CRITICAL', message, context, error);
  }

  // Operation logging with timing
  async logOperation<T>(
    operation: string,
    fn: () => Promise<T>,
    context?: Record<string, unknown>
  ): Promise<T> {
    const startTime = performance.now();
    this.info(`Starting operation: ${operation}`, context);

    try {
      const result = await fn();
      const duration = performance.now() - startTime;
      this.info(`Completed operation: ${operation}`, { ...context, duration });
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      this.error(`Failed operation: ${operation}`, error as Error, { ...context, duration });
      throw error;
    }
  }

  // API call logging
  logApiCall(method: string, url: string, status?: number, duration?: number, context?: Record<string, unknown>): void {
    this.info('API call', {
      operation: 'api_call',
      method,
      url,
      status,
      duration,
      ...context
    });
  }

  // User action logging
  logUserAction(action: string, context?: Record<string, unknown>): void {
    this.info('User action', {
      operation: 'user_action',
      action,
      ...context
    });
  }

  // Get current correlation info
  getCorrelationInfo(): { correlationId: string } {
    return {
      correlationId: this.correlationId
    };
  }

  // Update correlation ID (for new requests)
  updateCorrelationId(): void {
    this.correlationId = this.generateCorrelationId();
  }
}

// Export singleton instance
export const logger = new Logger();

// Export for testing
export { Logger };
