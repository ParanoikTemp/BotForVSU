from collections import deque
from typing import Iterable
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.read_only import EmptyCell
from openpyxl.utils.cell import coordinate_to_tuple
from schedules.models import *
from numpy import ndarray, full as numpy_full


ZeroBasedCellIndex = tuple[int, int]


def build_cells_matrix(sheet: Worksheet) -> ndarray:
    result = numpy_full((sheet.max_row, sheet.max_column), EmptyCell())

    for cells in sheet.iter_rows():
        for cell in cells:
            if isinstance(cell, EmptyCell):
                continue

            i, j = coordinate_to_tuple(cell.coordinate)
            result[i - 1][j - 1] = cell

    return result


def get_top_neighbour(cell: ZeroBasedCellIndex) -> ZeroBasedCellIndex:
    i, j = cell

    return (i - 1, j)


def get_left_neighbour(cell: ZeroBasedCellIndex) -> ZeroBasedCellIndex:
    i, j = cell

    return (i, j - 1)


def get_right_neighbour(cell: ZeroBasedCellIndex) -> ZeroBasedCellIndex:
    i, j = cell

    return (i, j + 1)


def get_bottom_neighbour(cell: ZeroBasedCellIndex) -> ZeroBasedCellIndex:
    i, j = cell

    return (i + 1, j)


def has_top_border(cells_matrix: ndarray, cell: ZeroBasedCellIndex) -> bool:
    i, j = cell
    n_i, n_j = get_top_neighbour(cell)

    if i <= 0 or n_i <= 0:
        return True

    cell_border = cells_matrix[i][j].border
    neighbour_cell_border = cells_matrix[n_i][n_j].border

    return cell_border and cell_border.top.border_style \
        or neighbour_cell_border and neighbour_cell_border.bottom.border_style


def has_left_border(cells_matrix: ndarray, cell: ZeroBasedCellIndex) -> bool:
    i, j = cell
    n_i, n_j = get_left_neighbour(cell)

    if j <= 0 or n_j <= 0:
        return True

    cell_border = cells_matrix[i][j].border
    neighbour_cell_border = cells_matrix[n_i][n_j].border

    return cell_border and cell_border.left.border_style \
        or neighbour_cell_border and neighbour_cell_border.right.border_style


def has_right_border(cells_matrix: ndarray, cell: ZeroBasedCellIndex) -> bool:
    i, j = cell
    n_i, n_j = get_right_neighbour(cell)

    if j >= cells_matrix.shape[1] or n_j >= cells_matrix.shape[1]:
        return True

    cell_border = cells_matrix[i][j].border
    neighbour_cell_border = cells_matrix[n_i][n_j].border

    return cell_border and cell_border.right.border_style \
        or neighbour_cell_border and neighbour_cell_border.left.border_style


def has_bottom_border(cells_matrix: ndarray, cell: ZeroBasedCellIndex) -> bool:
    i, j = cell
    n_i, n_j = get_bottom_neighbour(cell)

    if i >= cells_matrix.shape[0] or n_i >= cells_matrix.shape[0]:
        return True

    cell_border = cells_matrix[i][j].border
    neighbour_cell_border = cells_matrix[n_i][n_j].border

    return cell_border and cell_border.bottom.border_style \
        or neighbour_cell_border and neighbour_cell_border.top.border_style


def __build_cell_range(cells_matrix: ndarray, visited: ndarray, start_cell: ZeroBasedCellIndex) -> set[ZeroBasedCellIndex]:
    DIRECTIONS = [
        (has_top_border, get_top_neighbour),
        (has_left_border, get_left_neighbour),
        (has_right_border, get_right_neighbour),
        (has_bottom_border, get_bottom_neighbour)
    ]
    visited[start_cell] = True

    queue = deque([start_cell])
    nested_cells = set()

    while queue:
        cell = queue.pop()
        nested_cells.add(cell)

        for has_border, get_neighbour in DIRECTIONS:
            neighbour_cell = get_neighbour(cell)

            if has_border(cells_matrix, cell) or visited[neighbour_cell]:
                continue

            queue.append(neighbour_cell)
            visited[neighbour_cell] = True

    return nested_cells


def enumerate_cell_ranges(cells_matrix: ndarray) -> Iterable[set[ZeroBasedCellIndex]]:
    visited = numpy_full(cells_matrix.shape, False)

    for i in range(visited.shape[0]):
        for j in range(visited.shape[1]):
            if visited[i][j] or isinstance(cells_matrix[i][j], EmptyCell):
                continue

            yield __build_cell_range(cells_matrix, visited, (i, j))
