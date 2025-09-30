# Logging Configuration Documentation

## Overview

The ChroniSense application now includes comprehensive logging throughout the entire system. This logging infrastructure helps trace the flow of execution, identify problems, and debug errors effectively.

## Features

- **Centralized Configuration**: All logging is configured through `app/logging_config.py`
- **Dual Output**: Logs are written to both console (stdout) and rotating log files
- **Configurable Log Level**: Easily adjust verbosity via environment variable
- **Consistent Format**: All logs include timestamp, level, module name, function name, and message
- **Stack Traces**: Errors automatically include full stack traces for debugging
- **Log Rotation**: Log files automatically rotate when they reach 10MB (keeps last 5 files)

## Configuration

### Environment Variable

Set the log level using the `LOG_LEVEL` environment variable:

```bash
# In your .env file or environment
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Log Levels

- **DEBUG**: Detailed information for diagnosing problems (most verbose)
- **INFO**: Confirmation that things are working as expected (default)
- **WARNING**: Something unexpected happened, but the system continues
- **ERROR**: A more serious problem occurred
- **CRITICAL**: A very serious error that may prevent the system from continuing

### Log File Location

Logs are stored in: `/logs/chronisense.log`

The log file automatically rotates when it reaches 10MB, keeping the last 5 rotated files.

## What Gets Logged

### Application Lifecycle
- Application startup and initialization
- Flask extension initialization
- Blueprint registration
- Database connection setup

### Authentication
- Login attempts (successful and failed)
- Logout events
- User session loading

### API Endpoints
- All API endpoint calls with parameters
- Success/failure of operations
- Input validation errors
- Authorization checks

### Services

#### Chatbot Service
- Chatbot initialization
- Patient context retrieval
- Message processing
- Response generation
- Database operations

#### Vitals Simulator
- Simulation start/stop
- Vitals generation
- Data persistence
- Real-time data emission
- Alert generation

#### Web Scraper
- Health topic searches
- Content retrieval

### Database Operations
- Record creation
- Database commits
- Query execution
- Transaction errors

## Usage Examples

### Running with Different Log Levels

```bash
# Debug level (most verbose)
LOG_LEVEL=DEBUG python3 app.py

# Info level (default, recommended for production)
LOG_LEVEL=INFO python3 app.py

# Warning level (only warnings and errors)
LOG_LEVEL=WARNING python3 app.py

# Error level (only errors)
LOG_LEVEL=ERROR python3 app.py
```

### Viewing Logs

```bash
# View log file
cat logs/chronisense.log

# Follow log file in real-time
tail -f logs/chronisense.log

# View last 100 lines
tail -100 logs/chronisense.log

# Search for specific errors
grep "ERROR" logs/chronisense.log

# View logs for a specific module
grep "app.services.chatbot" logs/chronisense.log
```

## Log Format

Each log entry follows this format:
```
[YYYY-MM-DD HH:MM:SS] LEVEL [module.function:line] message
```

Example:
```
[2025-09-30 07:45:48] INFO [app.create_app:35] Initializing Flask extensions
[2025-09-30 07:45:48] ERROR [app.routes.api.get_vitals:44] Error retrieving vitals: Database connection failed
```

## Logged Components

### Modules with Comprehensive Logging

- ✅ `app/__init__.py` - Flask application factory
- ✅ `app.py` - Main entry point
- ✅ `app/routes/auth.py` - Authentication routes
- ✅ `app/routes/api.py` - API endpoints
- ✅ `app/services/chatbot.py` - AI chatbot service
- ✅ `app/services/vitals_simulator.py` - Vitals simulation
- ✅ `app/services/web_scraper.py` - Health knowledge scraping
- ✅ `init_db.py` - Database initialization

## Best Practices

### For Developers

1. **Use appropriate log levels**:
   - `logger.debug()` - Detailed diagnostic information
   - `logger.info()` - Important business events
   - `logger.warning()` - Unexpected situations that don't prevent operation
   - `logger.error()` - Errors that affect specific operations
   - `logger.critical()` - System-wide failures

2. **Include context in messages**:
   ```python
   # Good
   logger.info(f"User {username} logged in successfully, role={role}")
   
   # Not as helpful
   logger.info("Login successful")
   ```

3. **Always use exc_info=True for exceptions**:
   ```python
   try:
       # operation
   except Exception as e:
       logger.error(f"Operation failed: {e}", exc_info=True)
   ```

### For Operations

1. **Monitor log files regularly** for errors and warnings
2. **Set up log aggregation** for production environments
3. **Configure alerts** for critical errors
4. **Rotate logs** to manage disk space (already configured)

## Troubleshooting

### No logs appearing

1. Check that `LOG_LEVEL` is set appropriately
2. Verify the `logs/` directory exists and is writable
3. Ensure logging is initialized before other imports

### Too many logs

1. Increase the `LOG_LEVEL` to WARNING or ERROR
2. Adjust third-party library logging in `app/logging_config.py`

### Missing logs from specific modules

1. Ensure the module imports the logger: `logger = logging.getLogger(__name__)`
2. Check that logging calls use the correct logger instance

## Integration with Monitoring Tools

The logging system is compatible with popular monitoring and log aggregation tools:

- **Logstash/Elasticsearch/Kibana (ELK)**
- **Splunk**
- **Datadog**
- **New Relic**
- **CloudWatch (AWS)**
- **Stackdriver (GCP)**

Simply configure these tools to read from the log file or stdout.

## Future Enhancements

Potential improvements to the logging system:

- [ ] JSON-formatted logs for easier parsing
- [ ] Log aggregation service integration
- [ ] Performance metrics logging
- [ ] User activity audit logs
- [ ] Request/response logging middleware
- [ ] Correlation IDs for tracing requests across services
