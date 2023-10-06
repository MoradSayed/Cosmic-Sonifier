import speech_recognition as sr

class SR_Class:
    def __init__(self, tpf):     
        self.tpf_F_class = tpf

        # Initialize the recognizer
        self.recognizer = sr.Recognizer()

        # Call the listen_for_command function to start listening for voice commands
        # print("started")
        self.listen_for_command()

    # Define a function to listen for voice commands
    def listen_for_command(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source, phrase_time_limit=3)

        try:
            command = self.recognizer.recognize_google(audio).lower()
            # print("You said:", command)
            self.apply_command(command)

        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        # print("Done")

    def apply_command(self, command):
        # Check if the command matches your predefined command
        if "workspace" in command:
            self.tpf_F_class.page_switcher("Workspace")
        elif "home" in command:
            self.tpf_F_class.page_switcher("Home")
        elif "add" in command:
            self.tpf_F_class.page_switcher("Add")
        elif "open" in command:
            self.tpf_F_class.page_switcher("Open")
        elif "settings" in command:
            self.tpf_F_class.page_switcher("Settings")
        else:
            print("Command not recognized.")