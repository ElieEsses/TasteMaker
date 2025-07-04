from Modules.LLM.LLM import LLM
import openai
from openai import OpenAI

class ChatGPT(LLM):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def call_llm(
        self,
        prompt: str,
        sys_prompt: str = None,
        b64_image: str = None,
        img_type: str = "image/png",
        max_tokens: int = 4096,
        model: str = 'gpt-4o'
    ) -> str:
        
        # Build content list for the user message
        content = [{"type": "text", "text": prompt}]

        img_type = img_type.lower()
        valid_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if img_type not in valid_types:
            return f"Invalid image media type: {img_type}"
        
        if b64_image:
            try:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{img_type};base64,{b64_image}"
                    }
                })
            except Exception as e:
                return f"Image processing error: {e}"

        messages = []
        
        # Add system message if provided
        if sys_prompt:
            messages.append({
                "role": "system",
                "content": sys_prompt
            })
        
        messages.append({
            "role": "user",
            "content": content
        })

        request_params = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages
        }

        try:
            response = self.client.chat.completions.create(**request_params)
            
            # Check if response has expected structure
            if not response.choices or len(response.choices) == 0:
                return "Error: Empty response from API"
                
            return response.choices[0].message.content
            
        except openai.APIError as e:
            return f"API Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"