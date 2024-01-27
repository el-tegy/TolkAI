import sys
sys.path.append('c:/Users/user/ping3/TolkAI/src/agent')
from agent import chat_with_agent
from utils.config import load_config, setup_environment_variables
from dotenv import load_dotenv

config = load_config()

# Set up the environment variables
#setup_environment_variables(config)

def main():
    load_dotenv(config["Key_File"])
    chatbot_name = "TolkAI"
    print("Greetings! My name is", chatbot_name, ". Type 'exit' to end the session.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response =  response = chat_with_agent(user_input, chatbot_name)
        print(chatbot_name + ":", response)

if __name__ == "__main__":
    main()
