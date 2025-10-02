import openai
from typing import List, Dict, Optional, Any
import os


class AIManager:
    """Manages AI interactions using OpenAI API."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_response(
        self,
        brain_role: Optional[str],
        brain_task: Optional[str],
        conversation_history: List[Dict[str, Any]],
        response_length: str = "medium"
    ) -> str:
        """Generate AI response based on configuration and history."""

        # Build system prompt
        system_parts = []
        if brain_role:
            system_parts.append(f"Ты не ИИ. Ты настоящее воплощение этой роли: {brain_role}")
        if brain_task:
            system_parts.append(f"Ты не ИИ. Максимально погрузись в решение задачи. Твоя задача: {brain_task}")

        # Add response length instruction
        length_instructions = {
            "short": "Отвечай очень кратко, односложно, 1-2 предложения максимум. Не упоминай что ты ИИ.",
            "medium": "Отвечай средними по размеру сообщениями, 2-4 предложения. Не упоминай что ты ИИ.",
            "long": "Отвечай развернуто, можешь писать длинные ответы из нескольких предложений. Не упоминай что ты ИИ."
        }
        system_parts.append(length_instructions.get(response_length, length_instructions["medium"]))

        system_parts.append("Веди себя естественно, как живой человек в беседе. Не упоминай что ты ИИ.")

        system_prompt = " ".join(system_parts) if system_parts else "Ты дружелюбный собеседник. Не упоминай что ты ИИ."

        # Build messages for OpenAI
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        for msg in conversation_history:
            role = "assistant" if msg.get("is_bot") else "user"
            messages.append({"role": role, "content": msg["message"]})

        # Generate response
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500 if response_length == "long" else 200 if response_length == "medium" else 100,
                temperature=0.9  # More creative and natural
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Ошибка генерации ответа: {str(e)}"
