import subprocess
import json
import subprocess
import json
import asyncio

class CurlRequest:
    def __init__(self, url, payload, interface=None, headers=None):
        """
        Initializes the CurlRequest object with required parameters.
        
        :param url: The API endpoint URL.
        :param payload: A dictionary representing the JSON payload.
        :param interface: (Optional) The network interface IP to use for the request.
        :param headers: (Optional) Additional headers as a dictionary.
        """
        self.url = url
        self.payload = json.dumps(payload)
        self.interface = interface
        self.headers = headers or {
            "accept": "application/json",
            "content-type": "application/json"
        }

    async def send_request(self):
        """
        Constructs and executes the curl command.
        
        :return: The command output (stdout, stderr).
        """
        curl_cmd = [
            "curl",
            "--request", "POST",
            "--url", self.url,
            "--data", self.payload
        ]

        for key, value in self.headers.items():
            curl_cmd.extend(["--header", f"{key}: {value}"])

        if self.interface:
            curl_cmd.extend(["--interface", self.interface])

        process = await asyncio.create_subprocess_exec(
            *curl_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode()
        # return await subprocess.run(curl_cmd, capture_output=True, text=True)

class PyStimulusRequest(CurlRequest):
    def __init__(self, access_token, interface=None, intensity:int=100, stim:str=None):
        """
        Initializes a BeepRequest object for sending a beep stimulus.
        
        :param access_token: The access token for authorization.
        :param interface: (Optional) The network interface IP to use for the request.
        """

        stim_type = ["beep", "zap", "vibe"]
        if stim not in stim_type:
            raise ValueError(f"Invalid stimulus type: {stim}. Must be one of {stim_type}")
       
        url = "https://api.pavlok.com/api/v5/stimulus/send"
        if (isinstance(intensity, int) is False) or intensity > 100 or intensity < 0:
            raise ValueError("Intensity must be an integer between 0 and 100")
        
        payload = {
            "stimulus": {
                "stimulusType": stim,
                "stimulusValue": intensity,
                "reason": "test"
            }
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/json",
            "content-type": "application/json"
        }
        super().__init__(url, payload, interface, headers)

class PyStimTester:
    def __init__(self, stims:str='None', intensities:list=None):

        if not isinstance(intensities,list):
            raise ValueError("Intensities must be a list of integers between 0 and 100")
        
        self.stims = stims
        self.intensities = intensities

    async def start(self, show_output:bool=False):
        import time
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6bnVsbCwiaWQiOjMyNjI2NSwiZW1haWwiOiJtYWNpdmVybGFiQHUubm9ydGh3ZXN0ZXJuLmVkdSIsImlzX2FwcGxpY2F0aW9uIjpmYWxzZSwiZXhwIjoxNzcwNzUwNjczLCJzdWIiOiJhY2Nlc3MifQ.2YhAjTNxi186GK4_l_v3ue2W0VCotvdwzcKkvHVqDlc"
        interface = "10.105.229.251"
        for i in self.intensities:
            print(f'Sending stimulis: {self.stims} at intensity:', i)
            beep_request = PyStimulusRequest(access_token, interface, stim=self.stims, intensity=i)
            stdout, stderr = await beep_request.send_request()
            
            if show_output:
                print("Errors:", stderr if stderr else "No errors")
                print("Token Response:", stdout)


if __name__ == "__main__":
    import time
    times = []
    while True:
        t0 = time.time()
        pav = PyStimTester(stims='vibe', 
                     intensities=[100])
        asyncio.run(pav.start(show_output=False))
        times.append(time.time()-t0)
        print("Time taken:", times[-1])
        time.sleep(2)
    