from asynccapsolver import testAsyncCapSolver
import asyncio

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(testAsyncCapSolver('ENTER_YOUR_KEY_HERE'))
