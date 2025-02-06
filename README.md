# Async API for capsolver.com

## Installation

```bash
pip install git+https://github.com/optinsoft/asynccapsolver.git
```

## Usage

```python
from asynccapsolver import AsyncCapSolver
import asyncio

async def test(apiKey: str):
    capsolver = AsyncCapSolver(apiKey)
    print("getBalance\n", await capsolver.getBalance())    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test('PUT_YOUR_API_KEY_HERE'))
```
