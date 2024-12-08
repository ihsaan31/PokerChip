import streamlit as st
import random
import string
import json
import os

# File to store game data
GAMES_FILE = 'game_data.json'

# Load existing games or initialize
def load_games():
    if os.path.exists(GAMES_FILE):
        with open(GAMES_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save games to file
def save_games(games):
    with open(GAMES_FILE, 'w') as f:
        json.dump(games, f)

# Function to generate a unique game ID
def generate_game_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# Main Streamlit app
def main():
    st.title("Poker Chip Game Manager")
    
    # Load existing games
    games = load_games()

    st.sidebar.header("Game Setup")

    # Game creation form
    with st.sidebar.form("game_creator"):
        st.subheader("Create a New Game")
        game_name = st.text_input("Game Name")
        initial_chips = st.number_input("Initial chips per player", min_value=1, step=1, value=1000)
        max_players = st.number_input("Maximum number of players", min_value=2, step=1, value=4)
        submitted = st.form_submit_button("Create Game")
        
        if submitted:
            if game_name:
                game_id = generate_game_id()
                games[game_id] = {
                    "name": game_name,
                    "initial_chips": initial_chips,
                    "max_players": max_players,
                    "players": {},
                    "activity": [],
                    "pot": 0,
                }
                save_games(games)
                st.success(f"Game created! Share this Game ID: **{game_id}**")
            else:
                st.error("Game name cannot be empty.")

    # Section: Join a Game
    st.sidebar.header("Join a Game")
    game_id_input = st.sidebar.text_input("Enter Game ID")
    player_name = st.sidebar.text_input("Your Name")
    
    if st.sidebar.button("Join Game"):
        if game_id_input in games:
            game = games[game_id_input]
            if len(game["players"]) < game["max_players"]:
                if player_name not in game["players"]:
                    game["players"][player_name] = game["initial_chips"]
                    game["activity"].append(f"{player_name} has joined the game.")
                    save_games(games)
                    st.sidebar.success(f"Joined game {game_id_input} as {player_name}.")
                else:
                    st.sidebar.error("You are already in this game.")
            else:
                st.sidebar.error("The game is full.")
        else:
            st.sidebar.error("Invalid Game ID.")

    # Main section for game interaction
    if game_id_input and game_id_input in games and player_name:
        game = games[game_id_input]

        if player_name in game["players"]:
            st.subheader(f"Game: {game['name']} (ID: {game_id_input})")
            st.write(f"Welcome, {player_name}! Your chips: **{game['players'][player_name]}**")

            # Betting section
            st.write("### Manage Your Chips")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Bet 10"):
                    bet_amount = 10
                    if bet_amount <= game["players"][player_name]:
                        game["players"][player_name] -= bet_amount
                        game["pot"] += bet_amount
                        game["activity"].append(f"{player_name} bet {bet_amount} chips. Pot: {game['pot']}.")
                        save_games(games)
                        st.success("Bet placed successfully!")
                    else:
                        st.error("Not enough chips to place this bet.")

            with col2:
                if st.button("Bet 50"):
                    bet_amount = 50
                    if bet_amount <= game["players"][player_name]:
                        game["players"][player_name] -= bet_amount
                        game["pot"] += bet_amount
                        game["activity"].append(f"{player_name} bet {bet_amount} chips. Pot: {game['pot']}.")
                        save_games(games)
                        st.success("Bet placed successfully!")
                    else:
                        st.error("Not enough chips to place this bet.")

            with col3:
                if st.button("Bet 100"):
                    bet_amount = 100
                    if bet_amount <= game["players"][player_name]:
                        game["players"][player_name] -= bet_amount
                        game["pot"] += bet_amount
                        game["activity"].append(f"{player_name} bet {bet_amount} chips. Pot: {game['pot']}.")
                        save_games(games)
                        st.success("Bet placed successfully!")
                    else:
                        st.error("Not enough chips to place this bet.")

            # **Take Pot Section**
            st.write("### Take Chips from Pot")
            col1, col2 = st.columns(2)

            with col1:
                take_amount = st.number_input("Take Amount", min_value=0, max_value=game["pot"], step=1)
                if st.button("Take Selected"):
                    if take_amount > 0 and take_amount <= game["pot"]:
                        game["players"][player_name] += take_amount
                        game["pot"] -= take_amount
                        game["activity"].append(f"{player_name} took {take_amount} chips. Pot: {game['pot']}.")
                        save_games(games)
                        st.success("Chips taken successfully!")

            with col2:
                if st.button("Take All"):
                    if game["pot"] > 0:
                        game["players"][player_name] += game["pot"]
                        game["activity"].append(f"{player_name} took all the chips from the pot! Pot: 0.")
                        game["pot"] = 0
                        save_games(games)
                        st.success("All chips taken successfully!")

            # Display chip counts
            st.write("### Player Chip Counts")
            st.table({player: [chips] for player, chips in game["players"].items()})

            # Display the current pot
            st.write("### Current Pot")
            st.write(f"**{game['pot']} chips**")

            # Activity feed
            st.write("### Activity Feed")
            st.markdown("\n".join([f"- {activity}" for activity in game["activity"]]))

        else:
            st.error("You have not joined this game.")

if __name__ == "__main__":
    main()
