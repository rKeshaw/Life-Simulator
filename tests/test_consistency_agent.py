from infinite_lives.agents.consistency_agent import ConsistencyAgent
from infinite_lives.domain.models import AgentProposal, FactConfidence, WorldFact, WorldFactAssertCommand


def test_consistency_rejects_contradicting_fact():
    agent = ConsistencyAgent()
    fact = WorldFact(
        fact_id="f1",
        subject="sun",
        predicate="color",
        object="yellow",
        established_on_turn=1,
        confidence=FactConfidence.CERTAIN,
    )
    command = WorldFactAssertCommand(
        fact=WorldFact(
            fact_id="f2",
            subject="sun",
            predicate="color",
            object="blue",
            established_on_turn=2,
            confidence=FactConfidence.CERTAIN,
        )
    )
    proposal = AgentProposal(
        agent_id="x",
        proposed_commands=[command],
        confidence=0.9,
        touched_entities=["sun"],
        reasoning="test",
    )

    assert not agent.proposal_allowed(proposal, [(fact.subject, fact.predicate, fact.object)])
