# PLAN

1. Add a public diagnostics API for `RateLimiter` (current limit state, waiters queue size, active extra delay) to improve observability and incident analysis.
2. Standardize CLI/system log format with structured fields (for example `command`, `path`, `options`, `error_class`) to improve traceability in centralized logging.
3. Add strict validation for `project_name` and `root_namespace` in `startproject` (allowed characters, reserved names, valid Python package naming) to prevent generating invalid projects.
4. Decompose `StartProjectCommand` into dedicated layers (context building, template discovery, rendering, file writing) to improve maintainability and testability.
