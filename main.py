import streamlit as st
import random
import string

# Initialize session state for games
if "games" not in st.session_state:
    st.session_state["games"] = {}

# Function to generate a unique game ID
def generate_game_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# Section: Game Creator
st.title("Poker Chip Game Manager")
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
            st.session_state["games"][game_id] = {
                "name": game_name,
                "initial_chips": initial_chips,
                "max_players": max_players,
                "players": {},
                "activity": [],
                "pot": 0,
            }
            st.success(f"Game created! Share this Game ID: **{game_id}**")
        else:
            st.error("Game name cannot be empty.")

# Section: Join a Game
st.sidebar.header("Join a Game")
game_id_input = st.sidebar.text_input("Enter Game ID")
player_name = st.sidebar.text_input("Your Name")
if st.sidebar.button("Join Game"):
    if game_id_input in st.session_state["games"]:
        game = st.session_state["games"][game_id_input]
        if len(game["players"]) < game["max_players"]:
            if player_name not in game["players"]:
                game["players"][player_name] = game["initial_chips"]
                game["activity"].append(f"{player_name} has joined the game.")
                st.sidebar.success(f"Joined game {game_id_input} as {player_name}.")
            else:
                st.sidebar.error("You are already in this game.")
        else:
            st.sidebar.error("The game is full.")
    else:
        st.sidebar.error("Invalid Game ID.")

# Main section for game interaction
if game_id_input and game_id_input in st.session_state["games"] and player_name:
    game = st.session_state["games"][game_id_input]

    if player_name in game["players"]:
        st.subheader(f"Game: {game['name']} (ID: {game_id_input})")
        st.write(f"Welcome, {player_name}! Your chips: **{game['players'][player_name]}**")

        # Section: Bet or Take Chips
        st.write("### Manage Your Chips")

        # Display current bet amount and betting buttons in a grid layout
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

        # Place bet button
        if st.button("Place Bet"):
            bet_amount = st.session_state["bet_amount"]
            if bet_amount > 0 and bet_amount <= game["players"][player_name]:
                game["players"][player_name] -= bet_amount
                game["pot"] += bet_amount
                game["activity"].append(f"{player_name} bet {bet_amount} chips. Pot: {game['pot']}.")
                st.session_state["bet_amount"] = 0  # Reset after placing the bet
                st.success("Bet placed successfully!")
            else:
                st.error("Invalid bet amount. Check your available chips.")

        # Take chips input and buttons
        with st.expander("Take Chips"):
            take_amount = st.number_input("Take amount", min_value=0, max_value=game["pot"], step=1, key="take_amount")
            col5, col6 = st.columns(2)
            with col5:
                if st.button("Take Selected"):
                    if take_amount > 0:
                        game["players"][player_name] += take_amount
                        game["pot"] -= take_amount
                        game["activity"].append(f"{player_name} took {take_amount} chips. Pot: {game['pot']}.")
                        st.success("Chips taken successfully!")
            with col6:
                if st.button("Take All"):
                    if game["pot"] > 0:
                        game["players"][player_name] += game["pot"]
                        game["activity"].append(f"{player_name} took all the chips from the pot! Pot: 0.")
                        game["pot"] = 0
                        st.success("All chips taken successfully!")

        # Display chip counts in a tidy table
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
