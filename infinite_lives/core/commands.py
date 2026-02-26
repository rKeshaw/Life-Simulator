from __future__ import annotations

from infinite_lives.domain.models import (
    Command,
    PlayerActionCommand,
    WorldFact,
    WorldFactAssertCommand,
)


class CommandValidationError(ValueError):
    """Raised when a command is invalid for current state."""


def validate_player_action(command: PlayerActionCommand) -> None:
    if not command.raw_input.strip():
        raise CommandValidationError("Player action cannot be empty")


def validate_fact_assertion(command: WorldFactAssertCommand, existing_facts: list[WorldFact]) -> None:
    for fact in existing_facts:
        if (
            fact.subject == command.fact.subject
            and fact.predicate == command.fact.predicate
            and fact.object != command.fact.object
        ):
            raise CommandValidationError(
                f"Fact contradiction for {fact.subject}:{fact.predicate}"
            )


def validate_command(command: Command, existing_facts: list[WorldFact]) -> None:
    if isinstance(command, PlayerActionCommand):
        validate_player_action(command)
    elif isinstance(command, WorldFactAssertCommand):
        validate_fact_assertion(command, existing_facts)
