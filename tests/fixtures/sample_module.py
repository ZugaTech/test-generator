def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

async def fetch_data(url: str):
    """Simulates an async network call."""
    import asyncio
    await asyncio.sleep(0.1)
    return {"status": "success", "url": url}

class Calculator:
    def __init__(self, start: int = 0):
        self.value = start
    
    def multiply(self, x: int) -> int:
        self.value *= x
        return self.value

def complex_logic(x: int, y: int) -> str:
    if x > 0:
        if y > 0:
            return "both positive"
        else:
            return "x positive"
    elif x < 0:
        return "x negative"
    else:
        return "zero"

def get_config():
    # External dependency
    import os
    return os.environ.get("MODE", "dev")
