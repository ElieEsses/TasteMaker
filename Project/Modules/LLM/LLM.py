class LLM:
    def __init__(self, api_key:str):
        pass
    def call_llm(
        self,
        prompt: str,
        sys_prompt: str = None,
        b64_image: str = None,
        img_type: str = "image/png",
        max_tokens: int = 20000,
        model: str = None
    ) -> str:
        return ""