from typing import List, Optional, Tuple

def read_sudoku_from_file(filename: str) -> list:
    """
    Reads a Sudoku board from a text file and returns it as a 2D list of integers.
    Empty cells are represented by 0.
    
    :param filename: The path to the Sudoku text file.
    :return: A 9x9 2D list representing the Sudoku board.
    """
    board = []
    
    with open(filename, 'r') as file:
        for line in file:
            if '-' in line:
                continue
            
            row = [int(char) if char.isdigit() else 0 for char in line if char.isdigit() or char == '.']
            board.append(row)
    
    return board

def get_box_coordinates() -> List[List[Tuple[int, int]]]:
    """Return the list of coordinates for each 3x3 box in a 9x9 grid."""
    return [
        [(i + m, j + n) for m in range(3) for n in range(3)]
        for i in range(0, 9, 3) for j in range(0, 9, 3)
    ]

class Board:
    def __init__(self, initial_grid: Optional[List[List[int]]] = None) -> None:
        """Initialise a 9x9 Sudoku board, empty if no grid is provided."""
        self.grid: List[List[int]] = initial_grid or [[0] * 9 for _ in range(9)]
        self.fixed_cells: List[List[bool]] = [[bool(cell) for cell in row] for row in self.grid]

    def get_rows(self) -> List[List[int]]:
        return self.grid

    def get_columns(self) -> List[List[int]]:
        return [list(col) for col in zip(*self.grid)]

    def get_boxes(self) -> List[List[int]]:
        box_coords = get_box_coordinates()
        return [[self.grid[row][col] for row, col in box] for box in box_coords]

    def is_valid(self) -> bool:
        """Check board validity: no duplicates in rows, columns, or boxes."""
        def is_valid_group(group: List[int]) -> bool:
            elements = [num for num in group if num != 0]
            return len(elements) == len(set(elements))

        rows, cols, boxes = self.get_rows(), self.get_columns(), self.get_boxes()
        return all(is_valid_group(group) for group in rows + cols + boxes)

    def set_value(self, row: int, col: int, value: int) -> None:
        if not self.fixed_cells[row][col]:
            self.grid[row][col] = value

    def get_value(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def copy_board(self) -> 'Board':
        """Return a copy of the board."""
        return Board([row[:] for row in self.grid])

    def is_cell_fixed(self, row: int, col: int) -> bool:
        return self.fixed_cells[row][col]

    def get_modifiable_coordinates(self) -> List[Tuple[int, int]]:
        """Return coordinates of all modifiable cells."""
        return [(r, c) for r in range(9) for c in range(9) if not self.fixed_cells[r][c]]

    def reset(self) -> None:
        """Reset all modifiable cells to 0."""
        for row, col in self.get_modifiable_coordinates():
            self.grid[row][col] = 0

    def __repr__(self) -> str:
        """Return a string representation of the board."""
        board_str = "    " + "   ".join(map(str, range(9))) + "\n"  # Column numbers
        board_str += "  +" + "---+" * 9 + "\n"
        
        for i, row in enumerate(self.grid):
            row_str = f"{i} | " + " ".join(
                f"{cell if cell != 0 else '.'}" + " " + ("|" if (j + 1) % 3 == 0 else " ")
                for j, cell in enumerate(row)
            )
            board_str += row_str + "\n"
            if (i + 1) % 3 == 0:
                board_str += "  +" + "---+" * 9 + "\n"

        return board_str
