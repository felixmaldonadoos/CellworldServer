class StressTester:
    def __init__(self, ip="127.0.0.1", port=4791, test_duration=6, reset_interval=1, message_count=100):
        self.ip = ip
        self.port = port
        self.test_duration = test_duration  # Test duration in seconds
        self.reset_interval = reset_interval  # Time between resets in seconds
        self.message_count = message_count  # Number of messages to send
        self.failures = 0
        self.test_func = self.reset_model  # Set the function you want to test
        self.test_args = []  # Arguments for the test function (if any)

    def send_request(self, msg, timeout=10):
        try:
            with tcp.MessageClient(self.ip, self.port) as client:
                response = client.send_request(msg, timeout)
                return response
        except Exception as e:
            print(f"Error sending message: {e}")
            self.failures += 1
            return None

    def reset_model(self):
        print("Resetting model...")
        msg = tcp.Message(header="reset_model", body="")  # Just an example message
        response = self.send_request(msg)
        if response:
            print(f"Reset model response: {response.body}")
        else:
            print("Failed to reset model.")

    def send_messages(self):
        print("Sending messages...")
        for i in range(self.message_count):
            msg = tcp.Message(header="prey_step", body={"step": random.randint(1, 10)})  # Adjust body as needed
            response = self.send_request(msg)
            if response:
                print(f"Sent message {i+1}/{self.message_count}: {response.body}")
            else:
                print(f"Failed to send message {i+1}")
                self.failures += 1

    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.test_duration:
            print(f"Running stress test for {self.test_duration} seconds...")

            # Now, we properly reference the method
            self.test_func(*self.test_args)  # Call the function correctly

            time.sleep(self.reset_interval)

            self.send_messages()
            time.sleep(self.reset_interval)  # Wait before next reset

        print(f"Stress test completed with {self.failures} failures.")



    # create stress tester to see if it ever fails
    # can be done in a for loop (test for 6 hours)
    # ex. test-- reset, send 100 msgs, reset, send 100 msgs, etc etc.
    # stress test stress test stress test!!
    # Doesn't have to be neat on front end
    # Google how to test software, stress test mechanisms
    # a platform to test our functions
    # if i send something and expect something something back it should be what i expect
    # make flag: stop on fail-- save what happens (event, when it failed, print statement)