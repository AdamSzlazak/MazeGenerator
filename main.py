import pygame
import time
from queueHelper import PriorityQueue, AStarQueue
from math import inf
import random
from collections import deque
from constants import colors, constants
from node import Node
from button import Button


grid = []
for row in range(constants.ROWS):
    grid.append([])
    for column in range(constants.ROWS):
        grid[row].append(Node("blank"))

START_POINT = (
    random.randrange(2, constants.ROWS - 1, 2) - 1,
    random.randrange(2, constants.ROWS - 1, 2) - 1,
)
END = (
    random.randrange(2, constants.ROWS - 1, 2),
    random.randrange(2, constants.ROWS - 1, 2),
)

grid[START_POINT[0]][START_POINT[1]].update(nodetype="start")
grid[END[0]][END[1]].update(nodetype="end")

path_found = False
algorithm_run = False

pygame.init()

FONT = pygame.font.SysFont("arial", 6)

SCREEN_WIDTH = (
    constants.ROWS * (constants.WIDTH + constants.CELL_MARGIN)
    + constants.CELL_MARGIN * 2
)
SCREEN_HEIGHT = SCREEN_WIDTH + constants.BUTTON_HEIGHT * 3
WINDOW_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(WINDOW_SIZE)

mazeButton = Button(
    colors.GREY,
    0,
    SCREEN_WIDTH,
    SCREEN_WIDTH / 3,
    constants.BUTTON_HEIGHT * 3,
    "Generate maze",
)
resetButton = Button(
    colors.GREY,
    SCREEN_WIDTH / 3,
    SCREEN_WIDTH,
    SCREEN_WIDTH / 3,
    constants.BUTTON_HEIGHT * 3,
    "Reset",
)
dijkstraButton = Button(
    colors.GREY,
    (SCREEN_WIDTH / 3) * 2,
    SCREEN_WIDTH,
    SCREEN_WIDTH / 3,
    constants.BUTTON_HEIGHT,
    "Dijkstra",
)
dfsButton = Button(
    colors.GREY,
    (SCREEN_WIDTH / 3) * 2,
    SCREEN_WIDTH + constants.BUTTON_HEIGHT,
    SCREEN_WIDTH / 3,
    constants.BUTTON_HEIGHT,
    "DFS",
)
bfsButton = Button(
    colors.GREY,
    (SCREEN_WIDTH / 3) * 2,
    SCREEN_WIDTH + (constants.BUTTON_HEIGHT * 2),
    SCREEN_WIDTH / 3,
    constants.BUTTON_HEIGHT,
    "BFS",
)

pygame.display.set_caption("Pathfinder")

done = False

clock = pygame.time.Clock()

while not done:
    # region main loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            pressed = pygame.key.get_pressed()

            if dijkstraButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                pygame.display.flip()
                path_found = dijkstra(grid, START_POINT, END)
                grid[START_POINT[0]][START_POINT[1]].update(nodetype="start")
                algorithm_run = "dijkstra"

            elif dfsButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                pygame.display.flip()
                path_found = xfs(grid, START_POINT, END, x="d")
                grid[START_POINT[0]][START_POINT[1]].update(nodetype="start")
                algorithm_run = "dfs"

            elif bfsButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                pygame.display.flip()
                path_found = xfs(grid, START_POINT, END, x="b")
                grid[START_POINT[0]][START_POINT[1]].update(nodetype="start")
                algorithm_run = "bfs"

            elif resetButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(constants.ROWS):
                    for column in range(constants.ROWS):
                        if (row, column) != START_POINT and (row, column) != END:
                            grid[row][column].update(
                                nodetype="blank", is_visited=False, is_path=False
                            )

            elif mazeButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(constants.ROWS):
                    for column in range(constants.ROWS):
                        if (row, column) != START_POINT and (row, column) != END:
                            grid[row][column].update(
                                nodetype="blank", is_visited=False, is_path=False
                            )
                grid = prim()
    # endregion
    # region Game logic

    def clear_visited():
        excluded_nodetypes = ["start", "end", "wall", "mud"]
        for row in range(constants.ROWS):
            for column in range(constants.ROWS):
                if grid[row][column].nodetype not in excluded_nodetypes:
                    grid[row][column].update(
                        nodetype="blank", is_visited=False, is_path=False
                    )
                else:
                    grid[row][column].update(is_visited=False, is_path=False)
        update_gui(draw_background=False, draw_buttons=False)

    def update_path(algorithm_run=algorithm_run):
        clear_visited()

        valid_algorithms = ["dijkstra", "dfs", "bfs"]

        assert (
            algorithm_run in valid_algorithms
        ), f"last algorithm used ({algorithm_run}) is not in valid algorithms: {valid_algorithms}"

        if algorithm_run == "dijkstra":
            path_found = dijkstra(
                grid,
                START_POINT,
                END,
            )
        elif algorithm_run == "dfs":
            path_found = xfs(
                grid,
                START_POINT,
                END,
                x="d",
            )
        elif algorithm_run == "bfs":
            path_found = xfs(
                grid,
                START_POINT,
                END,
                x="b",
            )
        else:
            path_found = False
        return path_found

    def dict_move(from_dict, to_dict, item):
        to_dict[item] = from_dict[item]
        from_dict.pop(item)
        return from_dict, to_dict

    def get_neighbours(
        node,
        max_width=constants.ROWS - 1,
    ):
        neighbours = (
            ((min(max_width, node[0] + 1), node[1]), "+"),
            ((max(0, node[0] - 1), node[1]), "+"),
            ((node[0], min(max_width, node[1] + 1)), "+"),
            ((node[0], max(0, node[1] - 1)), "+"),
        )

        return (neighbour for neighbour in neighbours if neighbour[0] != node)

    def draw_square(row, column, grid=grid):
        pygame.draw.rect(
            screen,
            grid[row][column].color,
            [
                (constants.CELL_MARGIN + constants.HEIGHT) * column
                + constants.CELL_MARGIN,
                (constants.CELL_MARGIN + constants.HEIGHT) * row
                + constants.CELL_MARGIN,
                constants.WIDTH,
                constants.HEIGHT,
            ],
        )
        pygame.event.pump()

    def update_square(row, column):
        pygame.display.update(
            (constants.CELL_MARGIN + constants.WIDTH) * column + constants.CELL_MARGIN,
            (constants.CELL_MARGIN + constants.HEIGHT) * row + constants.CELL_MARGIN,
            constants.WIDTH,
            constants.HEIGHT,
        )
        pygame.event.pump()

    ### MAZE CREATION ALGORITHMS ###

    def prim(mazearray=False, start_point=False):
        if not mazearray:
            mazearray = []
            for row in range(constants.ROWS):
                mazearray.append([])
                for column in range(constants.ROWS):
                    if row % 2 != 0 and column % 2 != 0:
                        mazearray[row].append(Node("dormant"))
                    else:
                        mazearray[row].append(Node("wall"))
                    draw_square(row, column, grid=mazearray)

        n = len(mazearray) - 1

        if not start_point:
            start_point = (random.randrange(1, n, 2), random.randrange(1, n, 2))
            mazearray[start_point[0]][start_point[1]].update(nodetype="blank")

        draw_square(start_point[0], start_point[1], grid=mazearray)
        pygame.display.flip()

        walls = set()

        starting_walls = get_neighbours(start_point, n)

        for wall, ntype in starting_walls:
            if mazearray[wall[0]][wall[1]].nodetype == "wall":
                walls.add(wall)

        while len(walls) > 0:
            wall = random.choice(tuple(walls))
            visited = 0
            add_to_maze = []

            for wall_neighbour, ntype in get_neighbours(wall, n):
                if mazearray[wall_neighbour[0]][wall_neighbour[1]].nodetype == "blank":
                    visited += 1

            if visited <= 1:
                mazearray[wall[0]][wall[1]].update(nodetype="blank")

                draw_square(wall[0], wall[1], mazearray)
                update_square(wall[0], wall[1])
                time.sleep(0.0001)

                for neighbour, ntype in get_neighbours(wall, n):
                    if mazearray[neighbour[0]][neighbour[1]].nodetype == "dormant":
                        add_to_maze.append((neighbour[0], neighbour[1]))

                if len(add_to_maze) > 0:
                    cell = add_to_maze.pop()
                    mazearray[cell[0]][cell[1]].update(nodetype="blank")

                    draw_square(cell[0], cell[1], mazearray)
                    update_square(cell[0], cell[1])
                    time.sleep(0.0001)

                    for cell_neighbour, ntype in get_neighbours(cell, n):
                        if (
                            mazearray[cell_neighbour[0]][cell_neighbour[1]].nodetype
                            == "wall"
                        ):
                            walls.add(cell_neighbour)

            walls.remove(wall)

        mazearray[END[0]][END[1]].update(nodetype="end")
        mazearray[START_POINT[0]][START_POINT[1]].update(nodetype="start")

        return mazearray

    def gaps_to_offset():
        return [x for x in range(2, constants.ROWS, 3)]

    def recursive_division(chamber=None, gaps_to_offset=gaps_to_offset(), halving=True):
        sleep = 0.001
        sleep_walls = 0.001

        if chamber == None:
            chamber_width = len(grid)
            chamber_height = len(grid[1])
            chamber_left = 0
            chamber_top = 0
        else:
            chamber_width = chamber[2]
            chamber_height = chamber[3]
            chamber_left = chamber[0]
            chamber_top = chamber[1]

        if halving:
            x_divide = int(chamber_width / 2)
            y_divide = int(chamber_height / 2)

        if chamber_width < 3:
            pass
        else:
            for y in range(chamber_height):
                grid[chamber_left + x_divide][chamber_top + y].update(nodetype="wall")
                draw_square(chamber_left + x_divide, chamber_top + y)
                update_square(chamber_left + x_divide, chamber_top + y)
                time.sleep(sleep_walls)

        if chamber_height < 3:
            pass
        else:
            for x in range(chamber_width):
                grid[chamber_left + x][chamber_top + y_divide].update(nodetype="wall")
                draw_square(chamber_left + x, chamber_top + y_divide)
                update_square(chamber_left + x, chamber_top + y_divide)
                time.sleep(sleep_walls)

        if chamber_width < 3 and chamber_height < 3:
            return

        top_left = (chamber_left, chamber_top, x_divide, y_divide)
        top_right = (
            chamber_left + x_divide + 1,
            chamber_top,
            chamber_width - x_divide - 1,
            y_divide,
        )
        bottom_left = (
            chamber_left,
            chamber_top + y_divide + 1,
            x_divide,
            chamber_height - y_divide - 1,
        )
        bottom_right = (
            chamber_left + x_divide + 1,
            chamber_top + y_divide + 1,
            chamber_width - x_divide - 1,
            chamber_height - y_divide - 1,
        )

        chambers = (top_left, top_right, bottom_left, bottom_right)

        left = (chamber_left, chamber_top + y_divide, x_divide, 1)
        right = (
            chamber_left + x_divide + 1,
            chamber_top + y_divide,
            chamber_width - x_divide - 1,
            1,
        )
        top = (chamber_left + x_divide, chamber_top, 1, y_divide)
        bottom = (
            chamber_left + x_divide,
            chamber_top + y_divide + 1,
            1,
            chamber_height - y_divide - 1,
        )

        walls = (left, right, top, bottom)

        gaps = 3
        for wall in random.sample(walls, gaps):
            if wall[3] == 1:
                x = random.randrange(wall[0], wall[0] + wall[2])
                y = wall[1]
                if x in gaps_to_offset and y in gaps_to_offset:
                    if wall[2] == x_divide:
                        x -= 1
                    else:
                        x += 1
                if x >= constants.ROWS:
                    x = constants.ROWS - 1
            else:
                x = wall[0]
                y = random.randrange(wall[1], wall[1] + wall[3])
                if y in gaps_to_offset and x in gaps_to_offset:
                    if wall[3] == y_divide:
                        y -= 1
                    else:
                        y += 1
                if y >= constants.ROWS:
                    y = constants.ROWS - 1
            grid[x][y].update(nodetype="blank")
            draw_square(x, y)
            update_square(x, y)
            time.sleep(sleep)

        for chamber in enumerate(chambers):
            recursive_division(chamber)

    ### PATHFINDING ALGORITHMS ###

    def dijkstra(
        mazearray,
        start_point=(0, 0),
        goal_node=False,
        display=pygame.display,
    ):
        heuristic = 0
        distance = 0

        n = len(mazearray) - 1

        visited_nodes = set()
        unvisited_nodes = set([(x, y) for x in range(n + 1) for y in range(n + 1)])
        queue = AStarQueue()

        queue.push(distance + heuristic, distance, start_point)
        v_distances = {}

        if not goal_node:
            goal_node = (n, n)
        priority, current_distance, current_node = queue.pop()
        start = time.perf_counter()

        while current_node != goal_node and len(unvisited_nodes) > 0:
            if current_node in visited_nodes:
                if len(queue.show()) == 0:
                    return False
                else:
                    priority, current_distance, current_node = queue.pop()
                    continue

            for neighbour in get_neighbours(current_node, n):
                neighbours_loop(
                    neighbour,
                    mazearr=mazearray,
                    visited_nodes=visited_nodes,
                    unvisited_nodes=unvisited_nodes,
                    queue=queue,
                    v_distances=v_distances,
                    current_node=current_node,
                    current_distance=current_distance,
                )

            visited_nodes.add(current_node)
            unvisited_nodes.discard(current_node)

            v_distances[current_node] = current_distance

            if (current_node[0], current_node[1]) != start_point:
                mazearray[current_node[0]][current_node[1]].update(is_visited=True)
                draw_square(current_node[0], current_node[1], grid=mazearray)

                update_square(current_node[0], current_node[1])
                time.sleep(0.000001)

            if len(queue.show()) == 0:
                return False
            else:
                priority, current_distance, current_node = queue.pop()

        v_distances[goal_node] = current_distance + (1)
        visited_nodes.add(goal_node)

        trace_back(
            goal_node,
            start_point,
            v_distances,
            visited_nodes,
            n,
            mazearray,
        )

        end = time.perf_counter()
        num_visited = len(visited_nodes)
        time_taken = end - start

        print(
            f"Program finished in {time_taken:.4f} seconds after checking {num_visited} nodes. That is {time_taken/num_visited:.8f} seconds per node."
        )

        return False if v_distances[goal_node] == float("inf") else True

    def neighbours_loop(
        neighbour,
        mazearr,
        visited_nodes,
        unvisited_nodes,
        queue,
        v_distances,
        current_node,
        current_distance,
    ):
        neighbour, ntype = neighbour

        heuristic = 0

        if neighbour in visited_nodes:
            pass
        elif mazearr[neighbour[0]][neighbour[1]].nodetype == "wall":
            visited_nodes.add(neighbour)
            unvisited_nodes.discard(neighbour)
        else:
            modifier = mazearr[neighbour[0]][neighbour[1]].distance_modifier
            if ntype == "+":
                queue.push(
                    current_distance + (1 * modifier) + heuristic,
                    current_distance + (1 * modifier),
                    neighbour,
                )
            elif ntype == "x":
                queue.push(
                    current_distance + ((2**0.5) * modifier) + heuristic,
                    current_distance + ((2**0.5) * modifier),
                    neighbour,
                )

    def trace_back(
        goal_node,
        start_node,
        v_distances,
        visited_nodes,
        n,
        mazearray,
    ):
        path = [goal_node]

        current_node = goal_node

        while current_node != start_node:
            neighbour_distances = PriorityQueue()

            neighbours = get_neighbours(
                current_node,
                n,
            )

            try:
                distance = v_distances[current_node]
            except Exception as e:
                print(e)

            for neighbour, ntype in neighbours:
                if neighbour in v_distances:
                    distance = v_distances[neighbour]
                    neighbour_distances.push(distance, neighbour)

            distance, smallest_neighbour = neighbour_distances.pop()
            mazearray[smallest_neighbour[0]][smallest_neighbour[1]].update(is_path=True)

            draw_square(smallest_neighbour[0], smallest_neighbour[1], grid=mazearray)

            path.append(smallest_neighbour)
            current_node = smallest_neighbour

        pygame.display.flip()

        mazearray[start_node[0]][start_node[1]].update(is_path=True)

    def xfs(
        mazearray,
        start_point,
        goal_node,
        x,
        display=pygame.display,
    ):
        assert x == "b" or x == "d", "x should equal 'b' or 'd' to make this bfs or dfs"

        n = len(mazearray) - 1

        mydeque = deque()
        mydeque.append(start_point)
        visited_nodes = set([])
        path_dict = {start_point: None}

        while len(mydeque) > 0:
            if x == "d":
                current_node = mydeque.pop()
            elif x == "b":
                current_node = mydeque.popleft()

            if current_node == goal_node:
                path_node = goal_node
                while True:
                    path_node = path_dict[path_node]
                    mazearray[path_node[0]][path_node[1]].update(is_path=True)
                    draw_square(path_node[0], path_node[1], grid=mazearray)
                    update_square(path_node[0], path_node[1])
                    if path_node == start_point:
                        return True

            if mazearray[current_node[0]][current_node[1]].nodetype == "wall":
                continue

            if current_node not in visited_nodes:
                visited_nodes.add(current_node)
                mazearray[current_node[0]][current_node[1]].update(is_visited=True)
                draw_square(current_node[0], current_node[1], grid=mazearray)
                update_square(current_node[0], current_node[1])
                time.sleep(0.001)

                for neighbour, ntype in get_neighbours(current_node, n):
                    mydeque.append(neighbour)
                    if neighbour not in visited_nodes:
                        path_dict[neighbour] = current_node

        pygame.display.flip()
        return False

    grid[START_POINT[0]][START_POINT[1]].update(nodetype="start")
    grid[END[0]][END[1]].update(nodetype="end")

    def update_gui(draw_background=True, draw_buttons=True, draw_grid=True):
        if draw_background:
            screen.fill(colors.BLACK)
            pass

        if draw_buttons:
            dijkstraButton.draw(screen, (0, 0, 0))
            dfsButton.draw(screen, (0, 0, 0))
            bfsButton.draw(screen, (0, 0, 0))
            resetButton.draw(screen, (0, 0, 0))
            mazeButton.draw(screen, (0, 0, 0))

        if draw_grid:
            for row in range(constants.ROWS):
                for column in range(constants.ROWS):
                    color = grid[row][column].color
                    draw_square(row, column)

    update_gui()

    pygame.display.flip()

    clock.tick(60)
    # endregion
pygame.quit()
