import random

# Function to pick random problem numbers
def pick_random_problems(total_problems, number_to_pick):
    return sorted(random.sample(range(1, total_problems + 1), number_to_pick))

# Total number of problems
total_problems = 215

# Number of problems to pick
number_to_pick = 35

# Pick and sort random problems
random_problems = pick_random_problems(total_problems, number_to_pick)
print(f"Randomly selected problems (sorted): {random_problems}")
