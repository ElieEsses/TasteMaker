from Modules.LLM.LLM import LLM
import anthropic

class Claude(LLM):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def call_llm(
        self,
        prompt: str,
        sys_prompt: str = None,
        b64_image: str = None,
        img_type: str = "image/png",
        max_tokens: int = 20000,
        model: str = 'claude-sonnet-4-20250514'
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
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": img_type,
                        "data": b64_image
                    }
                })
            except Exception as e:
                return f"Image processing error: {e}"

        messages = [
            {
                "role": "user",
                "content": content
            }
        ]

        request_params = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages
        }

        if sys_prompt:
            request_params["system"] = sys_prompt

        try:
            response = self.client.messages.create(**request_params)
            
            # Check if response has expected structure
            if not response.content or len(response.content) == 0:
                return "Error: Empty response from API"
                
            return response.content[0].text
            
        except anthropic.APIError as e:
            return f"API Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"