import os
import openai
import random
import re

# Set up the OpenAI API client, plug API key in here
openai.api_key = "xxxxxxxxxxx"
#OpenAI detects if these keys are shared out and deactivates them if they are so I wasn't able to include a working key in here. I can try sending you a key separately if you need one.

# Persistent System Prompt (used to be named start_prompt)
system_prompt = [
    {"role": "system", "content": "You will act as a text adventure game. Only reply with game output and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. When I need to tell you something outside of the game, I will do so by putting text inside curly brackets. When you reply back outside of the game put your text inside curly brackets too. We will play this game in 2nd Person POV. The game's genre will be grimdark fantasy."},
]

#Deprecated
# starting_message = "Welcome to the Game. You are standing at the entrance of a dark cave. What do you want to do?"

start_scenes = [
    "You are standing at the entrance of a dark cave. What do you want to do?",
    "You find yourself in a bustling city market, surrounded by stalls selling all sorts of goods. What do you do?",
    "You wake up in a strange, unfamiliar room. The door is locked. sWhat do you do?",
    "You awaken in a moss-covered chamber, the air thick with ancient magic. What do you do?",
    "You stand at the entrance of a majestic elven city, its towering spires reaching for the heavens. What do you do?",
    "The door slams shut behind you as you enter a library, its shelves filled with forbidden tomes. What do you do?",
    "You stand above a valley. Sounds of battle echo below as two warring factions clash. What do you do?",
    "You arrive at the grand entrance of an imposing building, an arcane academy. What do you do?",
    "You are wading through a dense swamp. Mist curls atop the surface of the murky waters. What do you do?",
    "You find yourself in a sun-kissed meadow. The flowers are blooming and the air is sweet. What do you do?",
    "You find yourself in a bustling magical bazaar with all manner of oddities and artifacts. What do you do?",
    "High in the snowy peaks, amidst heavy snowfall and icy wind, you arrive at a hidden monastery. What do you do?",
    "You find yourself in a forsaken forest, shrouded in darkness. You hear a howl in the distance. What do you do?",
    "You find yourself inside a bustling tavern with a bard crooning in the background. What do you do?",
    "Surrounded by towering trees, you stumble upon a hidden clearing. What do you do?",
    "You find yourself on the vast plains, in the distance, something approaches. What do you do?",
    "You awaken in a damp dungeon cell, the sound of rattling chains echoing. What do you do?",
    "Amidst a vast desert, you come across an ancient temple buried beneath the sand. What do you do?",
    "You find yourself in a village square, surrounded by cheerful villagers going about their day. What do you do?",
    "Emerging from the dense forest, you spot a majestic castle standing proudly on a hill. What do you do?",
    "Venturing deep into a haunted graveyard, you hear eerie whispers carried by the chilling wind. What do you do?",
    "In a bustling tavern, you notice a mysterious figure lurking in the shadows. What do you do?",
    "On the deck of a weathered pirate ship, you hear the sound of cannons booming in the distance. What do you do?",
    "Adrift in the open sea, you spot a distant island with palm trees swaying in the breeze. What do you do?",
    # Add more later...
]

conversation = []
full_game_history = []

#This generates a randomized starting message
def generate_start_prompt():
    #print("DEBUG: Inside generate_start_prompt()") #DEBUG
    return [{"role": "assistant", "content": random.choice(start_scenes)}]

#This is the OpenAI API Call that generates story text for the game
def generate_text():
    global conversation

    # Calculate the total number of characters in the conversation
    total_chars = sum([len(message["content"]) for message in conversation])

    # If the total number of characters is above the threshold, remove the earliest messages until it's below the threshold
    max_chars = 2048  # Leave half the total tokens for the AI's response
    while total_chars > max_chars:
        removed_message = conversation.pop(0)  # Remove the earliest message
        total_chars -= len(removed_message["content"])

    # print("DEBUG: Inside generate_text()")
    # print("DEBUG: Sending the following conversation to OpenAI:")
    # for message in conversation:
    #     print(f'{message["role"]}: {message["content"]}')
    # print("DEBUG: Calling openai.ChatCompletion.create()")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            *system_prompt,
            *conversation  # Unpack the conversation list here       
        ],
        max_tokens=2048,
        n=1,
        temperature=0.7,        
        presence_penalty=0.35,
        frequency_penalty=0.35,
    )
    
    # print("DEBUG: Received a response from OpenAI")
    message = response['choices'][0]['message']['content']
    # print(f"DEBUG: Received the following message from OpenAI: {message}")
    return message

#Save Game Function
def save_game(full_game_history):
    project_folder = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(project_folder, "saved_game.txt")
    with open(file_path, "w") as file:
        for i in range(len(full_game_history)):
            if full_game_history[i]["role"] == "user":
                file.write("PLAYER: " + full_game_history[i]["content"] + "\n")
                if i+1 < len(full_game_history) and full_game_history[i+1]["role"] == "assistant":
                    file.write("GM: " + full_game_history[i+1]["content"] + "\n")
        file.write("\n")

#Load Game Function
def load_game():
    project_folder = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(project_folder, "saved_game.txt")
    conversation = []
    
    with open(file_path, "r") as file:
        content = file.read()
        messages = re.split("(PLAYER: |GM: )", content)
        for i in range(1, len(messages), 2):
            role = "user" if messages[i] == "PLAYER: " else "assistant"
            message_content = messages[i+1].strip()
            message = {"role": role, "content": message_content}
            conversation.append(message)
    
    return conversation

#Outer Game Loop
def main(load_saved_game=True):
    global conversation
    global full_game_history

    project_folder = os.path.dirname(os.path.abspath(__file__))
    save_file_path = os.path.join(project_folder, "saved_game.txt")

    while True:
        # Check if saved game exists
        if load_saved_game and os.path.isfile(save_file_path):
            print("A saved game file was found. Do you want to load it? (yes/no)")
            load_response = input("> ")
            if load_response.lower() in ["yes", "y"]:
                conversation = load_game()
                full_game_history = conversation.copy()  # Copy the loaded game to full_game_history
                print("Game Loaded!")
                print(conversation[-1]["content"])
            else:
                start_prompt = generate_start_prompt()
                print(start_prompt[-1]["content"] + "\n")  # Print the starting message to the user
                conversation = system_prompt + start_prompt
                full_game_history = generate_start_prompt()  # Initialize full_game_history the same as conversation
        else:
            start_prompt = generate_start_prompt()
            print(start_prompt[-1]["content"] + "\n")
            conversation = system_prompt + start_prompt
            full_game_history = generate_start_prompt()  # Initialize full_game_history the same as conversation
        
        # Inner Game loop
        while True:
            user_input = input("> ")

            # Check for special commands before appending user input to the conversation
            if user_input.lower() in ["save-game", "s"]:
                save_game(full_game_history)
                print("Game Saved!")
                continue  # Skip the rest of this loop iteration

            if user_input.lower() in ["load-game", "l"]:
                print("Loading...")
                full_game_history = load_game()
                if conversation:
                    print("Game Loaded!")
                    print(conversation[-1]["content"])
                else:
                    print("No saved game.")
                continue  # Skip the rest of this loop iteration

            if user_input.lower() in ["new-game", "n"]:
                print("Do you want to save the current game before starting a new one? (yes/no)")
                save_response = input("> ")
                if save_response.lower() in ["yes", "y"]:
                    save_game(full_game_history)
                    print("Game Saved!")
                print("Starting a new game...")
                main(load_saved_game=False)  # Restart the game without loading a saved game
                return  # Exit the current game instance after starting a new one
                        
            if user_input.lower() in ["quit-game", "x"]:
                print("Goodbye!")
                return  # Exit the entire game

            conversation.append({"role": "user", "content": user_input})
            full_game_history.append({"role": "user", "content": user_input})
            # print("DEBUG: Calling generate_text()")
            ai_response = generate_text()
            print(ai_response)
            conversation.append({"role": "assistant", "content": ai_response})
            full_game_history.append({"role": "assistant", "content": ai_response})

# Call main function to start the game
if __name__ == "__main__":
    main()
