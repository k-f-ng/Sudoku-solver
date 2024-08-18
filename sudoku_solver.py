from sudoku import Board, get_box_coordinates
import random
import math
from typing import Tuple

def cost_function(board: Board) -> int:
    """
    Calculate the total cost of a Sudoku board based on duplicates in rows, columns, and boxes.
    """
    def group_cost(group: list) -> int:
        """Return the cost for a single group (row, column, or box) as the number of repeats."""
        from collections import Counter
        counts = Counter(group)
        return sum(count - 1 if num != 0 else count for num, count in counts.items())

    total_cost = 0
    
    # Calculate row, column, and box costs
    for row in board.get_rows():
        total_cost += group_cost(row)
    for col in board.get_columns():
        total_cost += group_cost(col)
    for box in board.get_boxes():
        total_cost += group_cost(box)
    
    return total_cost

def coordinate_cost(board: Board, row: int, col: int) -> int:
    """
    Calculate the cost for an individual coordinate (row, col) on the Sudoku board.
    The cost is the sum of duplicates in the row, column, and box that the coordinate belongs to.
    """
    value = board.get_value(row, col)
    if value == 0:
        return 1

    def group_coordinate_cost(group: list) -> int:
        """Return the cost of a single group for a given value."""
        return group.count(value) - 1  # Subtract 1 for the original occurrence

    # Get the respective row, column, and box
    row_group = board.get_rows()[row]
    col_group = board.get_columns()[col]

    # Find the box that contains the (row, col)
    box_coords = get_box_coordinates()
    box_group = [board.get_value(r, c) for r, c in next(box for box in box_coords if (row, col) in box)]

    # Sum the costs from the row, column, and box
    return (
        group_coordinate_cost(row_group) +
        group_coordinate_cost(col_group) +
        group_coordinate_cost(box_group)
    )

def initialise_board(board: Board) -> None:
    """Fill the Sudoku board by ensuring no repeats in any row."""
    rows = board.get_rows()  # Get all rows once
    
    for row_idx, row_values in enumerate(rows):
        # Determine the missing numbers in the row
        missing_numbers = set(range(1, 10)) - set(row_values)
        
        # Fill in the missing numbers
        for col_idx in range(9):
            if board.get_value(row_idx, col_idx) == 0:
                board.set_value(row_idx, col_idx, missing_numbers.pop())

def select_coordinates(coord_costs: dict, board: Board) -> Tuple[tuple[int, int], tuple[int, int]]:
    """
    Select two coordinates:
    - coord1: A random coordinate selected with probabilities proportional to their costs.
    - coord2: Selected based on the chosen algorithm (either from the same row or uniformly from all modifiable coordinates).
    """
    coords = list(coord_costs.keys())
    weights = list(coord_costs.values())

    while True:
        # Select coord1 based on weighted probabilities
        coord1 = random.choices(coords, weights=weights, k=1)[0]

        # Algorithm 1: Select coord2 from the same row as coord1 (current implementation)
        # -------------------------------------------------------
        row1, col1 = coord1
        row_coords = [
            (row1, col) for col in range(9)
            if col != col1 and (row1, col) in coords
        ]
        if row_coords:
            coord2 = random.choice(row_coords)
            return coord1, coord2
        # # If no valid coord2 is found, loop to reselect coord1
        # -------------------------------------------------------

        # Algorithm 2: Select coord2 uniformly from all modifiable coords and ensure different value
        # -------------------------------------------------------
        while True:
            coord2 = random.choice(coords)
            if board.get_value(*coord2) != board.get_value(*coord1):
                return coord1, coord2
        # -------------------------------------------------------


def solver(board: Board, T: float = 2, max_iterations: int = 1_000_000, max_stagnation: int = 1500, decay: float = 0.999) -> bool:
    """
    Solve the Sudoku puzzle using simulated annealing.
    """
    T_initial = T
    initialise_board(board)
    current_cost = cost_function(board)
    min_cost = current_cost
    iterations = 0
    stagnation_counter = 0
    modifiable_coords = board.get_modifiable_coordinates()

    while current_cost > 0 and iterations < max_iterations:
        print(f"current_cost: {current_cost}, temperature: {T}")
        # Calculate the costs for all modifiable coordinates
        coord_costs = {coord: coordinate_cost(board, coord[0], coord[1]) for coord in modifiable_coords}

        # Select two different coordinates with probabilities proportional to their costs
        coord1, coord2 = select_coordinates(coord_costs, board)

        # Swap the values and evaluate the new cost
        swap_values(board, coord1, coord2)
        new_cost = cost_function(board)

        # Determine if we accept the swap
        delta_cost = new_cost - current_cost
        if delta_cost < 0 or random.random() < math.exp(-delta_cost / T):
            current_cost = new_cost
        else:
            # Revert the swap if not accepted
            swap_values(board, coord1, coord2)

        # Check if stagnation occurred
        if current_cost < min_cost:
            min_cost = current_cost
            stagnation_counter = 0 
        else:
            stagnation_counter += 1

        if stagnation_counter >= max_stagnation:
            T = T_initial
            min_cost = current_cost
            stagnation_counter = 0
        else:
            T *= decay

        iterations += 1

    return current_cost == 0

def swap_values(board: Board, coord1: tuple[int, int], coord2: tuple[int, int]) -> None:
    """Swap the values of two coordinates on the board."""
    row1, col1 = coord1
    row2, col2 = coord2
    val1 = board.get_value(row1, col1)
    val2 = board.get_value(row2, col2)
    board.set_value(row1, col1, val2)
    board.set_value(row2, col2, val1)
