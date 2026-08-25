from datetime import datetime, timezone
from typing import Optional, AsyncGenerator
from sih.domain.interaction.models import Conversation, Message
from sih.domain.intelligence.service import intelligence_service
from sih.domain.context.resolver import context_resolver
from sih.domain.planning.engine import planning_engine
from sih.domain.action.executor import action_executor
from sih.domain.memory.engine import memory_engine
from sih.domain.memory.models import MemoryType
from sih.core.exceptions import ApprovalRequiredError
from sih.domain.event_bus.bus import (
    event_bus, DomainEvent, EVENT_CONVERSATION_CREATED, EVENT_MESSAGE_RECEIVED
)

class InteractionService:
    def __init__(self):
        self._conversations: dict[str, Conversation] = {}
        self._messages: dict[str, list[Message]] = {}

    def create_conversation(self, user_id: str, workspace_id: str, title: str = "New Interaction") -> Conversation:
        conv = Conversation(user_id=user_id, workspace_id=workspace_id, title=title)
        self._conversations[conv.id] = conv
        self._messages[conv.id] = []
        return conv

    async def process_user_message(
        self,
        conversation_id: str,
        content: str,
        user_id: str,
        workspace_id: str
    ) -> Message:
        if conversation_id not in self._conversations:
            self.create_conversation(user_id, workspace_id, title=content[:30])

        user_msg = Message(
            conversation_id=conversation_id,
            sender_type="user",
            sender_id=user_id,
            content=content
        )
        self._messages[conversation_id].append(user_msg)

        await event_bus.publish(DomainEvent(
            event_type=EVENT_MESSAGE_RECEIVED,
            producer="InteractionService",
            user_id=user_id,
            workspace_id=workspace_id,
            payload={"conversation_id": conversation_id, "content": content}
        ))

        # 1. Context Resolution
        ctx = await context_resolver.resolve(
            user_id=user_id,
            workspace_id=workspace_id,
            conversation_id=conversation_id
        )

        # 2. Intent Extraction
        intent = await intelligence_service.extract_intent(content, context_summary=ctx.to_summary())

        # 3. DAG Plan Generation
        plan = await planning_engine.create_plan(intent, context=ctx)

        # 4. Execute Step DAG
        exec_results = []
        requires_approval_id = None
        approval_action_name = None

        for step in plan.steps:
            try:
                res = await action_executor.execute_action(
                    action_name=step.action_name,
                    parameters=step.parameters,
                    user_id=user_id,
                    workspace_id=workspace_id
                )
                exec_results.append(f"Step '{step.name}': {res.status.value}")
            except ApprovalRequiredError as e:
                requires_approval_id = e.approval_id
                approval_action_name = step.action_name
                exec_results.append(f"Step '{step.name}': HALTED (Requires Human Approval ID: {e.approval_id})")
                break
            except Exception as e:
                exec_results.append(f"Step '{step.name}': FAILED ({e})")
                break

        # 5. Format Response
        if requires_approval_id:
            response_text = (
                f"I parsed your intent as '{intent.type.value}' for target '{intent.target}'.\n\n"
                f"⚠️ Action '{approval_action_name}' requires human approval due to high risk.\n"
                f"Approval Request ID: {requires_approval_id}\n\n"
                f"Please review and approve in the Approval Queue."
            )
        else:
            response_text = (
                f"I processed your request: '{content}'.\n"
                f"Intent: {intent.type.value} | Target: {intent.target}\n"
                f"Steps Executed:\n" + "\n".join(f"- {r}" for r in exec_results)
            )

        # Store response
        assistant_msg = Message(
            conversation_id=conversation_id,
            sender_type="assistant",
            content=response_text
        )
        self._messages[conversation_id].append(assistant_msg)

        # Update Memory
        memory_engine.store(
            memory_type=MemoryType.EPISODIC,
            key=f"conv_{conversation_id}_{user_msg.id}",
            content={"prompt": content, "response": response_text},
            user_id=user_id,
            workspace_id=workspace_id
        )

        return assistant_msg

    def get_messages(self, conversation_id: str) -> list[Message]:
        return self._messages.get(conversation_id, [])

interaction_service = InteractionService()
