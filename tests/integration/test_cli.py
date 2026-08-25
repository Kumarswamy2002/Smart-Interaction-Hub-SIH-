import pytest
from sih.cli.main import handle_objective, handle_status, handle_approvals

@pytest.mark.asyncio
async def test_cli_objective_execution():
    await handle_objective("Prepare for project meeting", "cli-user", "cli-ws")
    await handle_status()
    await handle_approvals()
