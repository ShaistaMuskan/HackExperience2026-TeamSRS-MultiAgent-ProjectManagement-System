from enum import Enum


class MethodologyType(str, Enum):
    AGILE_SCRUM = "agile_scrum"
    KANBAN = "kanban"
    WATERFALL = "waterfall"
    PRINCE2 = "prince2"
    HYBRID = "hybrid"


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    SCHEDULE = "schedule"
    RESOURCE = "resource"
    BUDGET = "budget"
    SCOPE = "scope"
    TECHNICAL = "technical"
    DEPENDENCY = "dependency"
    QUALITY = "quality"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalActionType(str, Enum):
    CHANGE_DEADLINE = "change_deadline"
    REASSIGN_RESOURCE = "reassign_resource"
    DELETE_TASK = "delete_task"
    ESCALATION = "escalation"
    BUDGET_CHANGE = "budget_change"
    SCHEDULE_CHANGE = "large_schedule_modification"


class DependencyType(str, Enum):
    FINISH_TO_START = "finish_to_start"
    START_TO_START = "start_to_start"
    FINISH_TO_FINISH = "finish_to_finish"
    START_TO_FINISH = "start_to_finish"


class PhaseType(str, Enum):
    INITIATION = "initiation"
    PLANNING = "planning"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    CLOSURE = "closure"


class HealthStatus(str, Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    OFF_TRACK = "off_track"
    CRITICAL = "critical"
