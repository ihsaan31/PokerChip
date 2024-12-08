import streamlit as st
import random
import string
import pyrebase

# Firebase configuration
firebase_config = {
    "apiKey": "YOUR_FIREBASE_API_KEY",
    "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
    "databaseURL": "https://YOUR_PROJECT_ID.firebaseio.com",
    "storageBucket": "YOUR_PROJECT_ID.appspot.com",
}
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

# Function to generate a unique game ID
def generate_game_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# Create or Join a Game
st.title("Poker Chip Game Manager")

# Create a new game
st.sidebar.header("Create a Game")
with st.sidebar.form("game_creator"):
    game_name = st.text_input("Game Name")
    initial_chips = st.number_input("Initial chips per player", min_value=1, step=1, value=1000)
    max_players = st.number_input("Maximum number of players", min_value=2, step=1, value=4)
    submitted = st.form_submit_button("Create Game")
    if submitted:
        if game_name:
            game_id = generate_game_id()
            game_data = {
                "name": game_name,
                "initial_chips": initial_chips,
                "max_players": max_players,
                "players": {},
                "activity": [],
                "pot": 0,
            }
            db.child("games").child(game_id).set(game_data)
            st.success(f"Game created! Share this Game ID: **{game_id}**")
        else:
            st.error("Game name cannot be empty.")

# Join a game
st.sidebar.header("Join a Game")
game_id_input = st.sidebar.text_input("Enter Game ID")
player_name = st.sidebar.text_input("Your Name")
if st.sidebar.button("Join Game"):
    game_data = db.child("games").child(game_id_input).get().val()
    if game_data:
        if len(game_data["players"]) < game_data["max_players"]:
            if player_name not in game_data["players"]:
                game_data["players"][player_name] = game_data["initial_chips"]
                game_data["activity"].append(f"{player_name} has joined the game.")
                db.child("games").child(game_id_input).update(game_data)
                st.success(f"Joined game {game_id_input} as {player_name}.")
            else:
                st.error("You are already in this game.")
        else:
            st.error("The game is full.")
    else:
        st.error("Invalid Game ID.")

# Interact with the game
if game_id_input and player_name:
    game_data = db.child("games").child(game_id_input).get().val()
    if game_data:
        st.subheader(f"Game: {game_data['name']} (ID: {game_id_input})")
        st.write(f"Welcome, {player_name}! Your chips: **{game_data['players'].get(player_name, 0)}**")

        # Betting and chip management
        if "bet_amount" not in st.session_state:
            st.session_state["bet_amount"] = 0

        st.markdown(f"**Current Bet Amount:** {st.session_state['bet_amount']} chips")

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button("Bet 10"):
                st.session_state["bet_amount"] += 10
        with col2:
            if st.button("Bet 50"):
                st.session_state["bet_amount"] += 50
        with col3:
            if st.button("Bet 100"):
                st.session_state["bet_amount"] += 100
        with col4:
            if st.button("Reset Bet"):
                st.session_state["bet_amount"] = 0

        # Place bet
        if st.button("Place Bet"):
            bet_amount = st.session_state["bet_amount"]
            if bet_amount > 0 and bet_amount <= game_data["players"].get(player_name, 0):
                game_data["players"][player_name] -= bet_amount
                game_data["pot"] += bet_amount
                game_data["activity"].append(f"{player_name} bet {bet_amount} chips. Pot: {game_data['pot']}.")
                db.child("games").child(game_id_input).update(game_data)
                st.session_state["bet_amount"] = 0
                st.success("Bet placed successfully!")
            else:
                st.error("Invalid bet amount.")

        # Take chips
        with st.expander("Take Chips"):
            take_amount = st.number_input("Take amount", min_value=0, max_value=game_data["pot"], step=1)
            col5, col6 = st.columns(2)
            with col5:
                if st.button("Take Selected"):
                    if take_amount > 0:
                        game_data["players"][player_name] += take_amount
                        game_data["pot"] -= take_amount
                        game_data["activity"].append(f"{player_name} took {take_amount} chips. Pot: {game_data['pot']}.")
                        db.child("games").child(game_id_input).update(game_data)
                        st.success("Chips taken successfully!")
            with col6:
                if st.button("Take All"):
                    if game_data["pot"] > 0:
                        game_data["players"][player_name] += game_data["pot"]
                        game_data["activity"].append(f"{player_name} took all the chips! Pot: 0.")
                        game_data["pot"] = 0
                        db.child("games").child(game_id_input).update(game_data)
                        st.success("All chips taken successfully!")

        # Show game details
        st.write("### Player Chip Counts")
        st.table({player: [chips] for player, chips in game_data["players"].items()})
        st.write("### Current Pot")
        st.write(f"**{game_data['pot']} chips**")
        st.write("### Activity Feed")
        st.markdown("\n".join([f"- {activity}" for activity in game_data["activity"]]))
