import aiohttp
import ssl
import certifi
import json
import logging
from datetime import datetime
import asyncio

class AsyncCapSolverException(Exception):
    pass

class AsyncCapSolverTimeoutException(AsyncCapSolverException):
    pass

class AsyncCapSolverBadStatusException(AsyncCapSolverException):
    pass

class AsyncCapSolverNoSolutionException(AsyncCapSolverException):
    pass

class AsyncCapSolver:
    def __init__(self, client_key: str, app_id: int = 0, callback_url: str = None, api_url: str = 'https://api.capsolver.com/', 
                 logger: logging.Logger = None, http_timeout: int = 15, task_timeout: int = 120, get_result_delay: int = 5):
        self.client_key = client_key
        self.app_id = app_id
        self.callback_url = callback_url
        self.api_url = api_url
        self.logger = logger
        self.http_timeout = http_timeout        
        self.task_timeout = task_timeout
        self.get_result_delay = get_result_delay

    def checkResponse(self, respJson: dict):
        if respJson["errorId"] == 0:
            return respJson
        error_code = respJson["errorCode"] if "errorCode" in respJson else -1
        error_description = respJson["errorDescription"] if "errorDescription" in respJson else "Unknown error. " + json.dumps(respJson)
        raise AsyncCapSolverException(f"API error {error_code}: {error_description}")

    def logRequest(self, method: str, query: dict, response: dict):
        if not self.logger is None:
            self.logger.debug(
                'method: '+method+
                ', query: '+json.dumps(query)+
                ', response '+json.dumps(response)
            )

    async def doRequest(self, method: str, query: dict):
        url = self.api_url + method
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=conn, raise_for_status=False, timeout=aiohttp.ClientTimeout(total=self.http_timeout)) as session:
            async with session.post(url, data=json.dumps(query), timeout=self.http_timeout) as resp:
                if resp.status != 200:
                    respText = await resp.text()
                    self.logRequest(method, query, {'status':resp.status,'text':respText})
                    raise AsyncCapSolverException(f"Request failed:\nStatus Code: {resp.status}\nText: {respText}")
                try:
                    respText = await resp.text()
                    self.logRequest(method, query, {'status':resp.status,'text':respText})
                    respJson = json.loads(respText)
                except ValueError as e:
                    raise AsyncCapSolverException(f"Request failed: {str(e)}")
                return self.checkResponse(respJson)

    async def getBalance(self):
        method = "getBalance"
        query = {"clientKey": self.client_key}
        balance = await self.doRequest(method, query)
        return balance["balance"]
    
    async def createTask(self, task_data: dict):
        method = "createTask"
        query = {
            "clientKey": self.client_key, 
            "appId": self.app_id,
            "task": task_data
        }
        if self.callback_url:
            query["callbackUrl"] = self.callback_url
        return await self.doRequest(method, query)
    
    async def getTaskResult(self, task_id):
        method = "getTaskResult"
        query = {
            "clientKey": self.client_key,
            "taskId": task_id
        }
        return await self.doRequest(method, query)
    
    def extractTaskSolution(self, task_result):
        if not "solution" in task_result:
            raise AsyncCapSolverNoSolutionException(f"no solution: {json.dumps(task_result)}")
        return task_result["solution"]
    
    async def waitForTask(self, task_id, timeout: int = 0, get_result_delay: int = 0, log_processing: bool = False):
        if timeout == 0:
            timeout = self.task_timeout
        if get_result_delay == 0:
            get_result_delay = self.get_result_delay
        if get_result_delay <= 0:
            get_result_delay = 5
        t0 = datetime.now()
        noresult = True
        task_result = {}
        while noresult:
            await asyncio.sleep(get_result_delay)
            task_result = await self.getTaskResult(task_id)
            task_status = task_result["status"] if "status" in task_result else ""
            if task_status == "ready":
                noresult = False
            elif task_status == "processing":                
                noresult = True
                if log_processing:
                    if not self.logger is None:
                       self.logger.debug("processing...")
            else:
                raise AsyncCapSolverBadStatusException(f"bad task result status: {task_status}")
            if noresult:
                now = datetime.now()
                if (now-t0).total_seconds() >= timeout:
                    raise AsyncCapSolverTimeoutException("resolve captcha timed out")
        return self.extractTaskSolution(task_result)

    async def createImageToTextTask(self, img_str: str, website_url: str = None, module: str = None, score: float = None):
        task_data = {
            "type": "ImageToTextTask",
            "body": img_str
        }
        if website_url:
            task_data["websiteURL"] = website_url
        if module:
            task_data["module"] = module
        if score is not None:
            task_data["score"] = score
        return await self.createTask(task_data)
