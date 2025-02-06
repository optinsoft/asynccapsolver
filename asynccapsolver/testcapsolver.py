from .asynccapsolver import AsyncCapSolver, AsyncCapSolverException
from typing import Coroutine
import logging
from base64 import b64encode

async def testApi(apiName: str, apiRoutine: Coroutine):
    print(apiName)
    try:
        response = await apiRoutine
        print(response)
        return response
    except AsyncCapSolverException as e:
        print("AsyncCapSolverException:", e)
    return None

async def testImageToTextTask(capsolver: AsyncCapSolver):
    test_file_path = "test1.jpg"
    with open(test_file_path, 'rb') as img:
        img_str = img.read()
        img_str = b64encode(img_str).decode('ascii')
    task = await capsolver.createImageToTextTask(img_str, module="queueit")
    task_status = task["status"] if "status" in task else ""
    if task_status:
        print(f"task status: {task_status}")
    if task_status == "ready":
        solution = capsolver.extractTaskSolution(task)
    else:
        task_id = task["taskId"]
        solution = await capsolver.waitForTask(task_id, log_processing=True)
    return solution["text"]

async def testAsyncCapSolver(apiKey: str):
    logger = logging.Logger('testcapsolver')

    logger.setLevel(logging.DEBUG)

    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    log_path = './log/test.log'

    logFormatter = logging.Formatter(log_format)
    fileHandler = logging.FileHandler(log_path)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    capsolver = AsyncCapSolver(apiKey, logger=logger)

    print('--- asynccapsolver test ---')

    await testApi('getBalance', capsolver.getBalance())

    await testApi('imageToTextTask', testImageToTextTask(capsolver))
