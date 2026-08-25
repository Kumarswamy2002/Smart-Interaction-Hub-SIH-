class SIHError(Exception):
    """Base exception for Smart Interaction Hub."""
    def __init__(self, message: str, code: str = "SIH_ERROR", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class IdentityError(SIHError):
    """Identity & Auth errors."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="IDENTITY_ERROR", details=details)

class PermissionDeniedError(SIHError):
    """Permission & Policy errors."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="PERMISSION_DENIED", details=details)

class PolicyViolationError(SIHError):
    """Policy evaluation failure."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="POLICY_VIOLATION", details=details)

class ApprovalRequiredError(SIHError):
    """Operation halted pending human approval."""
    def __init__(self, message: str, approval_id: str, details: dict | None = None):
        d = details or {}
        d["approval_id"] = approval_id
        super().__init__(message, code="APPROVAL_REQUIRED", details=d)
        self.approval_id = approval_id

class ActionExecutionError(SIHError):
    """Action execution failure."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="ACTION_EXECUTION_FAILED", details=details)

class VerificationFailedError(SIHError):
    """Post-execution verification failure."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="VERIFICATION_FAILED", details=details)

class WorkflowExecutionError(SIHError):
    """Workflow execution failure."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="WORKFLOW_EXECUTION_FAILED", details=details)
