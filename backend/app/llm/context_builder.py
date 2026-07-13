"""ContextBuilder: constructs the smallest possible, token-minimized prompt contexts for CPU inference."""

import logging
from typing import Any, Union
from app.agents.agent import Agent, Relationship
from app.memory.memory import Memory

logger = logging.getLogger(__name__)


class ContextBuilder:
    """CPU-inference optimized LLM context builder for EchoCity.

    Filters, condenses, and formats agent traits, relationships, needs,
    and memories to construct highly compact prompt contexts.
    """

    @staticmethod
    def format_big_five(personality: dict[str, Any]) -> str:
        """Format Big Five personality traits in a highly compact format."""
        if not personality:
            return "N/A"
        big_five = personality.get("big_five", {})
        if not big_five:
            # Fallback to key-value or raw traits
            traits = personality.get("traits", [])
            return ", ".join(traits) if isinstance(traits, list) else str(traits)
        
        # Compact format: O:80, C:50, E:30, A:90, N:20
        parts = []
        for key, val in big_five.items():
            short_key = key[0].upper() if key else "?"
            # Convert float 0.0-1.0 or integer to percentage/integer
            if isinstance(val, float) and val <= 1.0:
                parts.append(f"{short_key}:{int(val * 100)}")
            else:
                parts.append(f"{short_key}:{val}")
        return ", ".join(parts)

    @staticmethod
    def format_speech_style(speech_style: dict[str, Any]) -> dict[str, Any]:
        """Condense speech style dictionary to minimize token count."""
        if not speech_style:
            return {"vocabulary": "normal", "tone": "conversational", "sentence_length": "medium", "favorite_expressions": []}
        return {
            "vocabulary": speech_style.get("vocabulary", "normal"),
            "tone": speech_style.get("tone", "conversational"),
            "sentence_length": speech_style.get("sentence_length", "medium"),
            "favorite_expressions": speech_style.get("favorite_expressions", [])[:2],  # Cap at 2 expressions
        }

    @staticmethod
    def format_relationships(relationships: dict[str, Any], nearby_agent_names: list[str]) -> str:
        """Filter and format relationships only for co-located/nearby agents."""
        if not relationships:
            return "None"
        
        parts = []
        for target_id, rel in relationships.items():
            # Standardize rel retrieval
            trust = getattr(rel, "trust", 0.5) if not isinstance(rel, dict) else rel.get("trust", 0.5)
            fear = getattr(rel, "fear", 0.0) if not isinstance(rel, dict) else rel.get("fear", 0.0)
            
            # Map agent_id back to display name if possible
            target_name = target_id.replace("_", " ").title()
            
            # Convert float to percentage
            trust_pct = int(trust * 100) if trust <= 1.0 else int(trust)
            fear_pct = int(fear * 100) if fear <= 1.0 else int(fear)
            
            parts.append(f"{target_name} (Trust:{trust_pct}%, Fear:{fear_pct}%)")
            
        return ", ".join(parts) if parts else "None"

    @staticmethod
    def filter_memories(memories: list[Any], reasoning_task: str, limit: int = 3) -> list[str]:
        """Filter and condense relevant memories based on the task type."""
        if not memories:
            return ["No significant memories."]
        
        task_lower = reasoning_task.lower().replace(" ", "_")
        filtered_summaries = []
        
        # 1. Gather all raw summary strings
        raw_memories = []
        for m in memories:
            if isinstance(m, str):
                raw_memories.append(m)
            elif isinstance(m, dict):
                raw_memories.append(m.get("summary", ""))
            elif hasattr(m, "summary"):
                raw_memories.append(getattr(m, "summary"))
        
        # Clean empty items
        raw_memories = [r.strip() for r in raw_memories if r.strip()]
        
        # 2. Filter memories based on task type
        if task_lower == "crime_decision":
            # Keep crime-related keywords
            keywords = ["debt", "secret", "theft", "silk", "steal", "gold", "market", "money"]
            for summary in raw_memories:
                if any(k in summary.lower() for k in keywords):
                    filtered_summaries.append(summary)
        elif task_lower == "witness_reasoning":
            # Keep event observations
            keywords = ["saw", "witnessed", "stole", "fled", "observed", "market"]
            for summary in raw_memories:
                if any(k in summary.lower() for k in keywords):
                    filtered_summaries.append(summary)
        elif task_lower in ["investigation_report", "memory_compression"]:
            # These tasks want case/witness files
            filtered_summaries = raw_memories
        else:
            # General/Gossip/Planning - keep recent/general
            filtered_summaries = raw_memories

        # If we filtered everything out, fall back to recent raw memories
        if not filtered_summaries:
            filtered_summaries = raw_memories

        # Remove duplicate summaries to save tokens
        seen = set()
        deduped = []
        for s in filtered_summaries:
            if s not in seen:
                seen.add(s)
                deduped.append(s)

        # Cap the number of memories strictly to save context window size
        return deduped[:limit]

    @classmethod
    def build(
        cls,
        reasoning_task: str,
        current_agent: Any = None,
        nearby_agents: list[Any] = None,
        relationships: dict[str, Any] = None,
        current_scene: Any = None,
        relevant_memories: list[Any] = None,
        current_needs: dict[str, Any] = None,
        stress: float = None,
        player_influence: Any = None,
    ) -> dict[str, Any]:
        """Construct the smallest possible context dictionary for the specified reasoning task.

        Args:
            reasoning_task: The target task category name.
            current_agent: Agent object or dict representing the subject agent.
            nearby_agents: List of Agent objects or dicts co-located with the subject.
            relationships: Relationship mappings.
            current_scene: Current location name or scene description.
            relevant_memories: List of Memory objects or summaries.
            current_needs: Current needs dictionary (energy, confidence, suspicion).
            stress: Subject agent's stress level.
            player_influence: Player nudge category and details.

        Returns:
            A token-minimized context dictionary matching the task specifications.
        """
        task_lower = reasoning_task.lower().replace(" ", "_")
        
        # 1. Resolve agent attributes (handle both objects and dicts)
        agent_name = "Observer"
        occupation = "System"
        personality_dict = {}
        speech_dict = {}
        secrets_dict = {}
        
        if current_agent:
            if isinstance(current_agent, dict):
                agent_name = current_agent.get("name", agent_name)
                occupation = current_agent.get("occupation", occupation)
                personality_dict = current_agent.get("personality", {})
                speech_dict = current_agent.get("speech_style", {})
                secrets_dict = current_agent.get("secrets", {})
                stress = stress if stress is not None else current_agent.get("stress", 0.0)
            else:
                agent_name = getattr(current_agent, "name", agent_name)
                occupation = getattr(current_agent, "occupation", occupation)
                personality_dict = getattr(current_agent, "personality", {})
                speech_dict = getattr(current_agent, "speech_style", {})
                secrets_dict = getattr(current_agent, "secrets", {})
                stress = stress if stress is not None else getattr(current_agent, "stress", 0.0)

        # Format Needs/Stress compactly
        stress_val = int(stress * 100) if (stress is not None and stress <= 1.0) else int(stress or 0)
        suspicion_val = 0
        energy_val = 100
        
        if current_needs:
            susp = current_needs.get("suspicion", 0.0)
            suspicion_val = int(susp * 100) if susp <= 1.0 else int(susp)
            eng = current_needs.get("energy", 1.0)
            energy_val = int(eng * 100) if eng <= 1.0 else int(eng)
        elif current_agent:
            if isinstance(current_agent, dict):
                susp = current_agent.get("suspicion", 0.0)
                suspicion_val = int(susp * 100) if susp <= 1.0 else int(susp)
                eng = current_agent.get("energy", 1.0)
                energy_val = int(eng * 100) if eng <= 1.0 else int(eng)
            else:
                susp = getattr(current_agent, "suspicion", 0.0)
                suspicion_val = int(susp * 100) if susp <= 1.0 else int(susp)
                eng = getattr(current_agent, "energy", 1.0)
                energy_val = int(eng * 100) if eng <= 1.0 else int(eng)

        needs_str = f"Stress:{stress_val}%, Suspicion:{suspicion_val}%, Energy:{energy_val}%"

        # Resolve Scene
        scene_str = "Cafe"
        if current_scene:
            if isinstance(current_scene, str):
                scene_str = current_scene
            elif isinstance(current_scene, dict):
                scene_str = current_scene.get("name", "Cafe")
            elif hasattr(current_scene, "name"):
                scene_str = getattr(current_scene, "name")

        # Resolve Nearby Agents names
        nearby_names = []
        if nearby_agents:
            for na in nearby_agents:
                if isinstance(na, str):
                    nearby_names.append(na)
                elif isinstance(na, dict):
                    nearby_names.append(na.get("name", ""))
                elif hasattr(na, "name"):
                    nearby_names.append(getattr(na, "name"))
        nearby_names = [n for n in nearby_names if n and n != agent_name]

        # 2. Build task-specific contexts
        if task_lower == "conversation":
            # Extract listener details
            listener_name = "Listener"
            listener_occupation = "Citizen"
            listener_speech = {}
            
            if nearby_agents and len(nearby_agents) > 0:
                first_listener = nearby_agents[0]
                if isinstance(first_listener, str):
                    listener_name = first_listener
                elif isinstance(first_listener, dict):
                    listener_name = first_listener.get("name", listener_name)
                    listener_occupation = first_listener.get("occupation", listener_occupation)
                    listener_speech = first_listener.get("speech_style", {})
                elif hasattr(first_listener, "name"):
                    listener_name = getattr(first_listener, "name")
                    listener_occupation = getattr(first_listener, "occupation", listener_occupation)
                    listener_speech = getattr(first_listener, "speech_style", {})

            # Filter to exactly 1 gossip memory
            mems = cls.filter_memories(relevant_memories, reasoning_task, limit=1)
            memory_summary = mems[0] if mems else "something interesting"
            
            return {
                "speaker": agent_name,
                "speaker_occupation": occupation,
                "speaker_speech": cls.format_speech_style(speech_dict),
                "listener": listener_name,
                "listener_occupation": listener_occupation,
                "listener_speech": cls.format_speech_style(listener_speech),
                "location": scene_str,
                "memory": memory_summary,
            }

        elif task_lower == "planning":
            schedule_act = "Going about duties"
            if isinstance(current_scene, dict) and "schedule_activity" in current_scene:
                schedule_act = current_scene["schedule_activity"]
            elif current_agent and not isinstance(current_agent, dict):
                # Retrieve active schedule entry if available
                goal = getattr(current_agent, "goal", None)
                if goal:
                    schedule_act = goal
            
            return {
                "agent_name": agent_name,
                "occupation": occupation,
                "traits": cls.format_big_five(personality_dict),
                "needs": needs_str,
                "time": current_scene.get("time", "06:00") if isinstance(current_scene, dict) else "06:00",
                "schedule_activity": schedule_act,
            }

        elif task_lower == "crime_decision":
            # Extract opportunity
            opportunity = "Unsupervised area"
            if isinstance(current_scene, dict) and "opportunity" in current_scene:
                opportunity = current_scene["opportunity"]
            
            # Format personality and secrets compactly
            pers = cls.format_big_five(personality_dict)
            sec = secrets_dict.get("regret", "N/A") if isinstance(secrets_dict, dict) else "N/A"
            
            return {
                "agent_name": agent_name,
                "opportunity": opportunity,
                "stress": f"{stress_val}%",
                "suspicion": f"{suspicion_val}%",
                "personality": pers,
                "secrets": sec,
            }

        elif task_lower == "witness_reasoning":
            mems = cls.filter_memories(relevant_memories, reasoning_task, limit=1)
            witnessed_event = mems[0] if mems else "observed suspicious activity"
            
            # Extract trust/fear metrics in target culprit
            culprit_id = "culprit"
            trust_val = 0.5
            fear_val = 0.0
            
            if player_influence and isinstance(player_influence, dict):
                culprit_id = player_influence.get("culprit_id", culprit_id)
            
            if relationships and culprit_id in relationships:
                rel = relationships[culprit_id]
                trust_val = getattr(rel, "trust", 0.5) if not isinstance(rel, dict) else rel.get("trust", 0.5)
                fear_val = getattr(rel, "fear", 0.0) if not isinstance(rel, dict) else rel.get("fear", 0.0)

            return {
                "agent_name": agent_name,
                "witnessed_event": witnessed_event,
                "trust_in_culprit": trust_val,
                "fear_of_culprit": fear_val,
            }

        elif task_lower == "diary_generation":
            mems = cls.filter_memories(relevant_memories, reasoning_task, limit=3)
            prev_diaries = []
            if player_influence:
                if isinstance(player_influence, list):
                    prev_diaries = player_influence
                elif isinstance(player_influence, dict):
                    prev_diaries = player_influence.get("previous_entries", [])
            
            return {
                "agent_name": agent_name,
                "occupation": occupation,
                "personality": personality_dict,  # Keep personality dict for rich diary template
                "recent_memories": mems,
                "previous_entries": prev_diaries[-2:],  # Cap at 2 previous entries
            }

        elif task_lower == "memory_compression":
            mems = cls.filter_memories(relevant_memories, reasoning_task, limit=5)
            formatted_memories = "\n".join(f"- {m}" for m in mems)
            
            return {
                "agent_name": agent_name,
                "memories": formatted_memories,
            }

        elif task_lower == "investigation_report":
            mems = cls.filter_memories(relevant_memories, reasoning_task, limit=3)
            formatted_evidence = "\n".join(f"- {m}" for m in mems)
            
            accused_name = "Suspect"
            if player_influence:
                if isinstance(player_influence, str):
                    accused_name = player_influence
                elif isinstance(player_influence, dict):
                    accused_name = player_influence.get("accused_name", accused_name)
                    
            return {
                "detective_name": agent_name,
                "accused_name": accused_name,
                "evidence_summaries": formatted_evidence,
            }

        else:
            # Default fallback: Higher Self Reasoning & general tasks
            details_str = str(player_influence) if player_influence else "Nudging cognitive paths."
            inf_type = "Cognitive Shift"
            
            if player_influence and isinstance(player_influence, dict):
                details_str = player_influence.get("details", details_str)
                inf_type = player_influence.get("type", inf_type)
            
            # Format compact state
            rel_str = cls.format_relationships(relationships, nearby_names)
            
            compact_state = {
                "goal": getattr(current_agent, "goal", "normal routine") if current_agent and not isinstance(current_agent, dict) else current_agent.get("goal", "normal routine") if current_agent else "normal routine",
                "needs": needs_str,
                "location": scene_str,
                "nearby_citizens": ", ".join(nearby_names) if nearby_names else "None",
                "relationships": rel_str,
            }
            
            return {
                "details": details_str,
                "agent_name": agent_name,
                "influence_type": inf_type,
                "current_state": compact_state,
            }
