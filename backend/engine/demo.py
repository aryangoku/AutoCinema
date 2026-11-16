"""Deterministic witness routes, executed through the real command dispatcher."""

from .models import Command, Result
from .service import GameEngine

TRUTH_ROUTE = (
    ("act_read_manifest", "item_manifest"),
    ("travel:loc_tavern", "loc_tavern"),
    ("talk:npc_elena", "npc_elena"),
    ("act_take_key", "item_key"),
    ("travel:loc_harbor", "loc_harbor"),
    ("travel:loc_lighthouse_ext", "loc_lighthouse_ext"),
    ("act_inspect_cable", "item_cable"),
    ("act_unlock_lighthouse", "door_lighthouse"),
    ("travel:loc_lighthouse_int", "loc_lighthouse_int"),
    ("act_read_journal", "item_journal"),
    ("travel:loc_lighthouse_ext", "loc_lighthouse_ext"),
    ("travel:loc_harbor", "loc_harbor"),
    ("travel:loc_tavern", "loc_tavern"),
    ("act_confront_elena", "npc_elena"),
    ("act_finish_truth", "npc_elena"),
)
UNRESOLVED_ROUTE = (("act_leave_town", "loc_harbor"),)


def issue(engine: GameEngine, action: str, target: str, command_id: str | None = None) -> Result:
    state = engine.state
    return engine.dispatch(
        Command(
            command_id=command_id or f"console:{state.state_version + 1}",
            session_id=engine.session_id,
            expected_state_version=state.state_version,
            action_id=action,
            target_id=target,
        )
    )
