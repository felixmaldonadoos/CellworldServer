import cellworld as cw 
import tcp_messages as tcp 
import json_cpp
import threading
import time 
import sys
import numpy as np

class ExperimentReplay: 
    def __init__(self):
        self._log_("init")
        self.port = None
        self.ip = None
        self.exp = None
        self.step_sz = None
        self.paused = True
        self.sleep_time = 1 # seconds
        self.auto_play = False
        self.__init_client__()
        pass 

    def load_log(self, log_file:str = None)->None:
        self._log_("load_log")
        if log_file is None: 
            self._log_("log_file is None")
            return
        self._log_(f"Loading: {log_file}")
        try: 
            self.exp = cw.Experiment.load_from_file(log_file)
        except FileNotFoundError as e: 
            self._log_(f"error: {e}")

        for episode in self.exp.episodes:
            self.step_sz = np.mean(np.gradient(episode.trajectories.get_agent_trajectory('prey').get('time_stamp')))
            if self.step_sz:
                print(f"step_sz:  {self.step_sz:0.4} | fs: {1/self.step_sz:0.4} hz") 
                break
        self._log_(f"loaded OK: {log_file}")
        return 
        
    def _log_(self, message:str = '')->None:
        print(f"[{self.__class__.__name__}] {message}")

    def __init_client__(self)->None:
        self._log_("init_client")
        if self.ip is None: 
            self.ip = '127.0.0.1'
            self._log_(f"ip set to {self.ip}")
        if self.port is None:
            self.port = 4791
            self._log_(f"port set to {self.port}")
        self.client = tcp.MessageClient()
        self.client.connect(ip='192.168.1.2', port=4791) 
        self.client.router.add_route("reset_response", self._reset_response_)
        print('[ExperimentReplay] Initialized client.')
        pass
        
    def _reset_response_(self, msg):
        print('[ExperimentReplay] Reset response received.')
        self.paused = False

    def update_progress_bar(self, iteration:int, total:int, length:int=50, msg=''):
        iteration += 1
        percent = (iteration / total) * 100
        filled_length = int(length * iteration // total)
        bar = '=' * filled_length + '-' * (length - filled_length)
        sys.stdout.write(f'\r[{bar}] {percent:.1f}% | {msg}')
        sys.stdout.flush()
        # if iteration == total:
        #     print('\n')

    def reset(self):
        if self.client is None: 
            self.__init_client__()

        print(self.client)
        if self.client is None: raise ValueError('Client is NONE')
        msg = tcp.Message(header="reset", body='')
        self.client.send_message(msg)
        self.paused = False

    def broadcast(self,x,y,r):
        
        msg = tcp.Message(header='prey_step',body=cw.Step(agent_name='prey',location=(0.5,0.5),rotation=180))
        self.client.send_message(msg)
        return 
        step = cw.Step(agent_name='prey',location=(x,y),rotation=r)
        msg = tcp.Message(header='prey_step',body=step)
        if self.client is None: raise ValueError('client is NONE')
        self.client.send_message(msg)
        print(f'sent message: {msg}')

    def run(self):
        if self.exp is None or self.exp.episodes is None:
            self._log_("no experiment loaded")
            return
        
        self._log_("=== Running ===\n")
        if self.exp is None: 
            self._log_("no experiment loaded")
            return
        
        if self.step_sz is None:
            self._log_("no step_sz")
            return
        
        # initialize client 
        # start replay
        curr_episode = 0
        self._log_(f"episodes: {len(self.exp.episodes)}")
        while True:
            if not self.paused:
                episode = self.exp.episodes[curr_episode]
                if episode is None: 
                    self._log_("no more episodes")
                    break
                t = episode.trajectories
                ht = t.get_agent_trajectory('prey')
                x = ht.get('location').get('x')
                y = ht.get('location').get('y')
                r = ht.get('rotation')
                if len(x) != len(y):
                    self._log_("x and y do not match")
                    break
                # send out the data 
                for i in range(len(x)):
                    self.broadcast(x[i], y[i],r[i])
                    # self._log_(f"Sending: x: {x[i]} | y: {y[i]}")
                    self.update_progress_bar(i, len(x), msg=f"Episodes completed: {curr_episode} / {len(self.exp.episodes)}")
                    time.sleep(self.step_sz)
                self.paused = True            
                curr_episode += 1
            else:
                if self.auto_play:
                    time.sleep(self.sleep_time)
                    print('Auto replay: True')
                    self.reset()
                else: 
                    input(f'\nPress Enter to continue... {curr_episode} / {len(self.exp.episodes)}')
                    # time.sleep(1)
                    self.reset()

if __name__ == "__main__":
    er = ExperimentReplay()
    er.load_log("logs/alberto2_fri_5_2_05022025_101332.json")
    er.ip = '127.0.0.1'
 
    er.auto_play = False
    er.run()

