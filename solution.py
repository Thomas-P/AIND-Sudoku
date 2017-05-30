assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # find all values, which has a length of two
    possible_naked_twins = [key for key in values if len(values[key]) == 2]
    # permute them and store also the value. The permutation is only available,
    # the values must be the same.
    find_by = [(key1, key2) \
               for i, key1 in enumerate(possible_naked_twins) \
               for key2 in possible_naked_twins[i::] \
               if key1 != key2 and values[key1] == values[key2]]
    # create an tuple of the digits to replace and the box, where to replace
    # the box is the square - {key1, key2]
    constraint_with_value = [(set(square) - {key[0], key[1]}, values[key[0]]) for key in find_by for square in unitlist if key[0] in square and key[1] in square]
    # check if the pairs are in the same box
    #if len(constraint_with_value)>0:
    #    print("Found Naked Value", constraint_with_value)
    for constraints, value in constraint_with_value:
        for peer in constraints:
            if len(values[peer])<2:
                continue
            for digit in value:
                values = assign_value(values, peer, values[peer].replace(digit, ''))
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    return values
    pass


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]


boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

# peer diagonal
diagonal_a = [rows[i]+cols[i] for i in range(0,9)]
diagonal_b = [rows[8-i]+cols[i] for i in range(0,9)]

# add as peers
for key in diagonal_a:
    peers[key] = set(list(peers[key]) + diagonal_a ) - {key}
for key in diagonal_b:
    peers[key] = set(list(peers[key]) + diagonal_b ) - {key}

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))
    pass

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    return [[values[a+b] for b in cols] for a in rows]

def eliminate(values):
    '''
    Eliminate all values from all constraint fields, which are solved
    :param values: values(dict): The sudoku in dictionary form
    :return: values(dict): The sudoku in dictionary form
    '''
    # get all keys for solved fields
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    # for each field key
    for box in solved_values:
        # get the digit
        digit = values[box]
        # remove the digit from all pears
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))
    return values


def only_choice(values):
    '''
    if a value is only found one time in a box, this is the solution for the field
    :param values:
    :return:
    '''
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    '''
        uses heuristics to reduce the search params
    :param values(dict): The sudoku in dictionary form
    :return:
    '''
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    key, value = min(values.items(), key=lambda x: len(x[1]) if len(x[1])>1 else 10)
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False),
    # return that answer!
    for i in value:
        copy = {key_:values[key_] for key_ in values}
        copy[key] = i
        solved = search(copy)
        if solved:
            return solved


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)
    pass

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
