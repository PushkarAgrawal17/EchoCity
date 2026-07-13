"""Prompt templates and prompt building logic for local Qwen generation."""

import json
from typing import Any


class PromptBuilder:
    """Constructs system and user prompts for local AI cognition."""

    @staticmethod
    def build_gossip_prompt(
        speaker_name: str,
        speaker_occupation: str,
        speaker_speech: dict[str, Any],
        listener_name: str,
        listener_occupation: str,
        listener_speech: dict[str, Any],
        location_name: str,
        memory_summary: str,
    ) -> tuple[str, str]:
        """Build prompts to generate a natural gossip dialogue between two citizens."""
        system_prompt = (
            "You are a narrative writer for EchoCity. Write natural, character-authentic dialogue. "
            "Return ONLY a JSON object in this format:\n"
            '{\n  "dialogue": "dialogue text"\n}\n'
            "Do not include any explanation outside the JSON."
        )

        user_prompt = (
            f"Generate a short, natural conversation between {speaker_name} (a {speaker_occupation}) "
            f"and {listener_name} (a {listener_occupation}) at the {location_name}.\n\n"
            f"{speaker_name} is sharing this rumor/information with {listener_name}: '{memory_summary}'.\n\n"
            f"Speaker Speech Details:\n"
            f"- Vocabulary: {speaker_speech.get('vocabulary', 'normal')}\n"
            f"- Tone: {speaker_speech.get('tone', 'conversational')}\n"
            f"- Sentence length: {speaker_speech.get('sentence_length', 'medium')}\n"
            f"- Favorite expressions: {speaker_speech.get('favorite_expressions', [])}\n\n"
            f"Listener Speech Details:\n"
            f"- Vocabulary: {listener_speech.get('vocabulary', 'normal')}\n"
            f"- Tone: {listener_speech.get('tone', 'conversational')}\n"
            f"- Sentence length: {listener_speech.get('sentence_length', 'medium')}\n"
            f"- Favorite expressions: {listener_speech.get('favorite_expressions', [])}\n\n"
            f"Write a brief back-and-forth dialogue (2-4 lines total) that feels organic, "
            f"incorporating their speech styles and personalities. Output ONLY the JSON."
        )

        return system_prompt, user_prompt

    @staticmethod
    def build_scene_prompt(
        location_name: str,
        agents_info: list[dict[str, Any]],
        recent_events: list[str],
    ) -> tuple[str, str]:
        """Build prompts to generate a novel-style narrative event for co-located agents."""
        system_prompt = (
            "You are a novelist writing immersive, detailed scenes for EchoCity. "
            "Return ONLY a JSON object in this format:\n"
            '{\n  "narrative": "scene description text"\n}\n'
            "Do not include any explanation outside the JSON."
        )

        agents_str = "\n".join(
            f"- {a['name']} (a {a['occupation']}): feeling {a['emotion']} (stress: {a['stress']:.1%}, suspicion: {a['suspicion']:.1%}). "
            f"Goal: {a['goal']}. Secrets/Regrets: {a.get('secrets', {}).get('regret', '')}."
            for a in agents_info
        )

        recent_str = "\n".join(f"- {e}" for e in recent_events[-5:]) if recent_events else "None."

        user_prompt = (
            f"Generate a detailed, single-paragraph novel-style description of what is happening at the {location_name}.\n\n"
            f"People present:\n{agents_str}\n\n"
            f"Recent history context:\n{recent_str}\n\n"
            f"Describe their subtle interactions, movements, and body language (e.g. rubs a wedding ring, straightens a tie, checks a note) "
            f"to show their inner stress and goals. Output ONLY the JSON."
        )

        return system_prompt, user_prompt

    @staticmethod
    def build_diary_prompt(
        agent_name: str,
        occupation: str,
        personality: dict[str, Any],
        recent_memories: list[str],
        previous_entries: list[str],
    ) -> tuple[str, str]:
        """Build prompts to generate a character-authentic diary entry."""
        system_prompt = (
            f"You are writing a private diary entry for {agent_name}, a {occupation} in EchoCity. "
            "Return ONLY a JSON object in this format:\n"
            '{\n  "diary": "diary entry text"\n}\n'
            "Do not include any explanation outside the JSON."
        )

        memories_str = "\n".join(f"- {m}" for m in recent_memories)
        previous_str = "\n".join(f"- {p}" for p in previous_entries[-2:]) if previous_entries else "None."

        user_prompt = (
            f"Write a short, intimate diary entry for {agent_name} at the end of the day.\n\n"
            f"Big Five traits: {personality.get('big_five', {})}\n"
            f"Specific traits: {personality.get('traits', {})}\n\n"
            f"Memories/thoughts from today:\n{memories_str}\n\n"
            f"Previous entries context:\n{previous_str}\n\n"
            f"Write in the first-person ('I'). The tone should be private, reflective, and align with their speech style "
            f"and personality. Output ONLY the JSON."
        )

        return system_prompt, user_prompt

    @staticmethod
    def build_influence_prompt(
        agent_name: str,
        influence_type: str,
        details: str,
        current_state: dict[str, Any],
    ) -> tuple[str, str]:
        """Build prompts to generate narrative for player cognitive influence."""
        system_prompt = (
            "You are a narrative writer describing subtle mental shifts in citizens. "
            "Return ONLY a JSON object in this format:\n"
            '{\n  "narrative": "influence narrative text"\n}\n'
            "Do not include any explanation outside the JSON."
        )

        user_prompt = (
            f"{agent_name} has just received a subtle cognitive nudge from 'The Higher Self'.\n"
            f"Influence type: {influence_type.upper()} ({details})\n\n"
            f"Current state:\n"
            f"- Goal: {current_state.get('goal')}\n"
            f"- Emotion: {current_state.get('emotion')}\n"
            f"- Stress: {current_state.get('stress')}\n"
            f"- Suspicion: {current_state.get('suspicion')}\n\n"
            f"Write a brief description of how this nudge feels to {agent_name} (e.g. a sudden flash of clarity, "
            f"a sudden wave of comfort, a voice echoing in their mind) and how it shifts their mood or focus. "
            f"Output ONLY the JSON."
        )

        return system_prompt, user_prompt

    @staticmethod
    def build_question_prompt(
        agent_name: str,
        occupation: str,
        traits: dict[str, Any],
        secrets: dict[str, Any],
        memories_summaries: list[str]
    ) -> tuple[str, str]:
        """Build prompts to generate a character-authentic response to being questioned."""
        system_prompt = (
            f"You are writing a dialogue response for {agent_name}, a {occupation} in EchoCity, reacting to being questioned. "
            "Return ONLY a JSON object in this format:\n"
            '{\n  "dialogue": "dialogue text"\n}\n'
            "Do not include any explanation outside the JSON."
        )

        memories_str = "\n".join(f"- {m}" for m in memories_summaries)
        user_prompt = (
            f"Generate a brief speech reaction for {agent_name} who is being questioned.\n\n"
            f"Here is what they know/remember:\n{memories_str}\n\n"
            f"Their personality traits: {traits}\n"
            f"Their secrets/fears: {secrets}\n\n"
            f"Write a short dialogue response (1-2 sentences) of them speaking to the interviewer. "
            f"If they have secrets or fears, they should sound cagey, defensive, or anxious. Output ONLY the JSON."
        )

        return system_prompt, user_prompt
