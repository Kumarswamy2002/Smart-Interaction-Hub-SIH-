from sih.domain.intent.models import Intent, IntentType
from sih.domain.context.models import UnifiedContext
from sih.domain.planning.models import Plan, PlanStep, StepStatus
from sih.domain.policy.engine import policy_engine
from sih.domain.event_bus.bus import event_bus, DomainEvent, EVENT_PLAN_CREATED

class PlanningEngine:
    """Planning Engine converting Intent into executable DAG Plan with policy evaluation."""

    async def create_plan(self, intent: Intent, context: UnifiedContext | None = None) -> Plan:
        steps: list[PlanStep] = []

        if intent.type == IntentType.PREPARE_MEETING:
            step1 = self._build_step("Find Meeting Details", "find_meeting", intent.target)
            step2 = self._build_step("Retrieve Participants", "find_participants", intent.target, dependencies=[step1.id])
            step3 = self._build_step("Search Related Documents", "read_knowledge", intent.target, dependencies=[step1.id])
            step4 = self._build_step("Find Pending Tasks", "read_private", "Tasks", dependencies=[step1.id])
            step5 = self._build_step("Generate Briefing Notes", "create_task", "Briefing Document", dependencies=[step2.id, step3.id, step4.id])
            step6 = self._build_step("Send Preparation Email", "send_email", "Participants", dependencies=[step5.id])
            steps.extend([step1, step2, step3, step4, step5, step6])

        elif intent.type == IntentType.CREATE_TASK:
            step1 = self._build_step("Create Task", "create_task", intent.target, parameters=intent.parameters)
            steps.append(step1)

        elif intent.type == IntentType.EXECUTE_WORKFLOW:
            step1 = self._build_step("Execute Workflow", "start_workflow", intent.target, parameters=intent.parameters)
            steps.append(step1)

        elif intent.type == IntentType.SEND_MESSAGE:
            step1 = self._build_step("Send External Message", "send_message", intent.target, parameters=intent.parameters)
            steps.append(step1)

        else:
            step1 = self._build_step("Query System", "read_knowledge", intent.target)
            steps.append(step1)

        plan = Plan(
            intent_id=intent.id,
            raw_prompt=intent.raw_prompt,
            user_id=context.user_id if context else None,
            workspace_id=context.workspace_id if context else None,
            steps=steps
        )

        await event_bus.publish(DomainEvent(
            event_type=EVENT_PLAN_CREATED,
            producer="PlanningEngine",
            user_id=plan.user_id,
            workspace_id=plan.workspace_id,
            payload={"plan_id": plan.id, "total_steps": len(steps)}
        ))

        return plan

    def _build_step(
        self,
        name: str,
        action_name: str,
        target: str,
        parameters: dict | None = None,
        dependencies: list[str] | None = None
    ) -> PlanStep:
        policy_res = policy_engine.evaluate_action(action_name, parameters=parameters)
        return PlanStep(
            name=name,
            action_name=action_name,
            target=target,
            parameters=parameters or {},
            dependencies=dependencies or [],
            risk_level=policy_res.risk_level,
            requires_approval=policy_res.requires_approval
        )

planning_engine = PlanningEngine()
