import argparse
import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sih.domain.interaction.service import interaction_service
from sih.domain.task.service import task_platform
from sih.domain.approval.service import approval_service
from sih.domain.action.executor import action_executor
from sih.domain.observability.service import observability_platform

console = Console()

async def handle_objective(prompt: str, user_id: str, workspace_id: str):
    console.print(Panel(f"[bold cyan]Smart Interaction Hub[/bold cyan]\nObjective: [bold yellow]'{prompt}'[/bold yellow]", title="SIH Intent Pipeline"))
    
    conv = interaction_service.create_conversation(user_id, workspace_id, title=prompt[:30])
    msg = await interaction_service.process_user_message(conv.id, prompt, user_id, workspace_id)
    
    console.print(Panel(msg.content, title="[bold green]Execution Result[/bold green]"))

async def handle_tasks():
    tasks = task_platform.list_tasks()
    table = Table(title="Smart Interaction Hub - Active Tasks")
    table.add_column("Task ID", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Priority")
    table.add_column("Status")

    for t in tasks:
        table.add_row(t.id[:8], t.title, t.priority.value, t.status.value)
    
    console.print(table)

async def handle_approvals():
    approvals = approval_service.list_pending()
    table = Table(title="Pending Human Approvals Queue")
    table.add_column("Approval ID", style="bold yellow")
    table.add_column("Action", style="bold cyan")
    table.add_column("Target")
    table.add_column("Risk Level", style="bold red")

    for a in approvals:
        table.add_row(a.id, a.action_name, a.target, a.risk_level.value)

    console.print(table)

async def handle_approve_action(approval_id: str):
    try:
        app_req = await approval_service.approve(approval_id, reviewer_user_id="cli-admin")
        console.print(f"[bold green]Approved approval request {approval_id}![/bold green] Executing action...")
        res = await action_executor.execute_action(
            action_name=app_req.action_name,
            parameters=app_req.parameters,
            user_id=app_req.requester_user_id,
            workspace_id=app_req.workspace_id,
            approval_id=app_req.id
        )
        console.print(Panel(f"Action '{app_req.action_name}' executed. Verification: {res.verification_passed}", title="Execution Complete"))
    except Exception as e:
        console.print(f"[bold red]Error approving request:[/bold red] {e}")

async def handle_status():
    health = observability_platform.get_health()
    console.print(Panel(
        f"Status: [bold green]{health.status}[/bold green]\n"
        f"Uptime: {health.uptime_seconds:.2f}s\n"
        f"Components: {health.components}",
        title="SIH Health Status"
    ))

def main():
    parser = argparse.ArgumentParser(description="Smart Interaction Hub CLI")
    subparsers = parser.add_subparsers(dest="command")

    obj_parser = subparsers.add_parser("objective", help="Execute natural language objective")
    obj_parser.add_argument("prompt", type=str, help="Objective prompt")

    subparsers.add_parser("tasks", help="List active tasks")
    subparsers.add_parser("approvals", help="List pending approvals")
    
    app_parser = subparsers.add_parser("approve", help="Approve pending request")
    app_parser.add_argument("approval_id", type=str, help="Approval ID")

    subparsers.add_parser("status", help="Check system health")

    args = parser.parse_args()

    if args.command == "objective":
        asyncio.run(handle_objective(args.prompt, "cli-user", "cli-workspace"))
    elif args.command == "tasks":
        asyncio.run(handle_tasks())
    elif args.command == "approvals":
        asyncio.run(handle_approvals())
    elif args.command == "approve":
        asyncio.run(handle_approve_action(args.approval_id))
    elif args.command == "status":
        asyncio.run(handle_status())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
