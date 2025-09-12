import random

player_choices = ("rock", "paper", "scissors")


while True:
    player_1 = input("Enter rock, paper or scissors: ").strip().lower()
    player_2 = random.choice(player_choices)


    #DRAW
    if player_1 == player_2:
        print(f"player_1 is {player_1} vs player_2 is {player_2}: 'The game is a draw!")

        #Player 1 Wins!
    elif player_1 == 'rock' and player_2 == 'scissors':
        print(f"player_1 is {player_1} vs player_2 is {player_2}: \nPlayer 1 Wins!")
    elif player_1 == 'scissors' and player_2 == 'paper':
        print(f"player_1 is {player_1} vs player_2 is {player_2}: \nPlayer 1 Wins!")
    elif player_1 == 'paper' and player_2 == 'rock':
        print(f"player_1 is {player_1} vs player_2 is {player_2}: \nPlayer 1 Wins!")

        #Player 2 Wins!
    elif player_2 == 'rock' and player_1 == 'scissors':
        print(f"player_1 is {player_1} vs player_2 is {player_2}: \nPlayer 2 Wins!")
    elif player_2 == 'scissors' and player_1 == 'paper':
        print(f"player_1 is {player_1} vs player_2 is {player_2}: \nPlayer 2 Wins!")
    elif player_2 == 'paper' and player_1 == 'rock':
        print(f"player_1 is {player_1} vs player_2 is {player_2}: \nPlayer 2 Wins!")

    elif player_1 not in player_choices:
        print("Invalid choice, thank you for playing! Game Over")
    
    play_again = input("Play again? (y/n): ").strip().lower()
    if play_again == 'no' or play_again == 'n':
        print('Game Over! Thank you for playing!')
        break