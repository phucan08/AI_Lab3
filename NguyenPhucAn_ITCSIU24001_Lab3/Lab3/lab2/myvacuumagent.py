from lab2.vacuum import *

DEBUG_OPT_DENSEWORLDMAP = False

AGENT_STATE_UNKNOWN = 0
AGENT_STATE_WALL = 1
AGENT_STATE_CLEAR = 2
AGENT_STATE_DIRT = 3
AGENT_STATE_HOME = 4

AGENT_DIRECTION_NORTH = 0
AGENT_DIRECTION_EAST = 1
AGENT_DIRECTION_SOUTH = 2
AGENT_DIRECTION_WEST = 3

def direction_to_string(cdr):
    cdr %= 4
    return  "NORTH" if cdr == AGENT_DIRECTION_NORTH else\
            "EAST"  if cdr == AGENT_DIRECTION_EAST else\
            "SOUTH" if cdr == AGENT_DIRECTION_SOUTH else\
            "WEST" #if dir == AGENT_DIRECTION_WEST

"""
Internal state of a vacuum agent
"""
class MyAgentState:

    def __init__(self, width, height):

        # Initialize perceived world state
        self.world = [[AGENT_STATE_UNKNOWN for _ in range(height)] for _ in range(width)]
        self.world[1][1] = AGENT_STATE_HOME

        # Agent internal state
        self.last_action = ACTION_NOP
        self.direction = AGENT_DIRECTION_EAST
        self.pos_x = 1
        self.pos_y = 1

        # Metadata
        self.world_width = width
        self.world_height = height
        print(width, height)

    """
    Update perceived agent location
    """

    def update_position(self, bump):
        if self.last_action != ACTION_FORWARD:
            return
        if bump:
            return  # do NOT move into wall

        if self.direction == AGENT_DIRECTION_EAST:
            self.pos_x += 1
        elif self.direction == AGENT_DIRECTION_SOUTH:
            self.pos_y += 1
        elif self.direction == AGENT_DIRECTION_WEST:
            self.pos_x -= 1
        elif self.direction == AGENT_DIRECTION_NORTH:
            self.pos_y -= 1

    """
    Update perceived or inferred information about a part of the world
    """

    def update_world(self, x, y, info):
        if 0 <= x < self.world_width and 0 <= y < self.world_height:
            self.world[x][y] = info

    """
    Dumps a map of the world as the agent knows it
    """
    def print_world_debug(self):
        for y in range(self.world_height):
            for x in range(self.world_width):
                if self.world[x][y] == AGENT_STATE_UNKNOWN:
                    print("?" if DEBUG_OPT_DENSEWORLDMAP else " ? ", end="")
                elif self.world[x][y] == AGENT_STATE_WALL:
                    print("#" if DEBUG_OPT_DENSEWORLDMAP else " # ", end="")
                elif self.world[x][y] == AGENT_STATE_CLEAR:
                    print("." if DEBUG_OPT_DENSEWORLDMAP else " . ", end="")
                elif self.world[x][y] == AGENT_STATE_DIRT:
                    print("D" if DEBUG_OPT_DENSEWORLDMAP else " D ", end="")
                elif self.world[x][y] == AGENT_STATE_HOME:
                    print("H" if DEBUG_OPT_DENSEWORLDMAP else " H ", end="")

            print() # Newline
        print() # Delimiter post-print

"""
Vacuum agent
"""
class MyVacuumAgent(Agent):

    def __init__(self, world_width, world_height, log, search_algorithm="BFS"):
        super().__init__(self.execute)

        self.initial_random_actions = 10
        self.iteration_counter = world_width * world_height * 10
        self.state = MyAgentState(world_width, world_height)
        self.log = log

        #add new params for Lab2
        self.route = []  # acts like stack
        self.home_pos = (1, 1)
        self.steps = 0
        self.cleaned = 0
        self.score = -1000
        self.terminated = False
        self.nodes_explored = 0
        self.search_algorithm = search_algorithm
        self.result_reported = False
        self.result_data = None

    def update_score(self, action, shutdown=False):
        if self.terminated:
            return  # prevent ANY further scoring

        if shutdown:
            self.score += 1000
            self.terminated = True  # lock system
        elif action == ACTION_SUCK:
            self.score += 100
        else:
            self.score -= 1

    def move_to_random_start_position(self, bump):
        action = random()

        self.initial_random_actions -= 1
        self.state.update_position(bump)

        if action < 0.1666666:   # 1/6 chance
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            self.update_score(ACTION_TURN_LEFT)
            return ACTION_TURN_LEFT
        elif action < 0.3333333: # 1/6 chance
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            self.update_score(ACTION_TURN_RIGHT)
            return ACTION_TURN_RIGHT
        else:                    # 4/6 chance
            self.state.last_action = ACTION_FORWARD
            self.update_score(ACTION_FORWARD)
            return ACTION_FORWARD

    def bfs(self, return_home=False):
        if return_home:
            target = self.home_pos
        else:
            # find closest unknown
            unknowns = [(x,y) for x in range(self.state.world_width) for y in range(self.state.world_height) if self.state.world[x][y] == AGENT_STATE_UNKNOWN]
            if not unknowns:
                self.route = []
                return
            start = (self.state.pos_x, self.state.pos_y)
            target = min(unknowns, key=lambda p: abs(p[0]-start[0]) + abs(p[1]-start[1]))
        start = (self.state.pos_x, self.state.pos_y)
        if start == target:
            self.route = []
            return
        # BFS
        from collections import deque
        queue = deque([start])
        came_from = {start: None}
        visited = set([start])
        explored_this_search = 0
        found = False
        while queue:
            current = queue.popleft()
            explored_this_search += 1
            if current == target:
                found = True
                break
            for dx, dy in [(0,-1), (1,0), (0,1), (-1,0)]:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < self.state.world_width and 0 <= ny < self.state.world_height and (nx, ny) not in visited and self.state.world[nx][ny] != AGENT_STATE_WALL:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
                    came_from[(nx, ny)] = current
        self.nodes_explored += explored_this_search
        if not found:
            self.route = []
            return
        # reconstruct path
        path = []
        current = target
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        self.route = path

    def astar(self, return_home=False):
        if return_home:
            target = self.home_pos
        else:
            # find closest unknown
            unknowns = [(x,y) for x in range(self.state.world_width) for y in range(self.state.world_height) if self.state.world[x][y] == AGENT_STATE_UNKNOWN]
            if not unknowns:
                self.route = []
                return
            start = (self.state.pos_x, self.state.pos_y)
            target = min(unknowns, key=lambda p: abs(p[0]-start[0]) + abs(p[1]-start[1]))
        start = (self.state.pos_x, self.state.pos_y)
        if start == target:
            self.route = []
            return
        # A*
        import heapq
        
        def heuristic(pos):
            # Manhattan distance heuristic
            return abs(pos[0] - target[0]) + abs(pos[1] - target[1])
        
        # Priority queue: (f_score, counter, position)
        open_set = [(heuristic(start), 0, start)]
        came_from = {start: None}
        g_score = {start: 0}
        visited = set()
        explored_this_search = 0
        counter = 1
        found = False
        
        while open_set:
            current_f, _, current = heapq.heappop(open_set)
            
            if current in visited:
                continue
            visited.add(current)
            explored_this_search += 1
            
            if current == target:
                found = True
                break
            
            for dx, dy in [(0,-1), (1,0), (0,1), (-1,0)]:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < self.state.world_width and 0 <= ny < self.state.world_height and (nx, ny) not in visited and self.state.world[nx][ny] != AGENT_STATE_WALL:
                    tentative_g = g_score[current] + 1
                    
                    if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                        g_score[(nx, ny)] = tentative_g
                        came_from[(nx, ny)] = current
                        f_score = tentative_g + heuristic((nx, ny))
                        heapq.heappush(open_set, (f_score, counter, (nx, ny)))
                        counter += 1
        
        self.nodes_explored += explored_this_search
        if not found:
            self.route = []
            return
        # reconstruct path
        path = []
        current = target
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        self.route = path

    def move_to(self, target):
        cx, cy = self.state.pos_x, self.state.pos_y
        tx, ty = target
        dx = tx - cx
        dy = ty - cy
        # Determine target direction
        if abs(dx) > abs(dy):
            target_dir = AGENT_DIRECTION_EAST if dx > 0 else AGENT_DIRECTION_WEST
        else:
            target_dir = AGENT_DIRECTION_SOUTH if dy > 0 else AGENT_DIRECTION_NORTH
        # Compute turn
        turn = (target_dir - self.state.direction) % 4

        if turn == 1 or turn == 2:
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            self.update_score(ACTION_TURN_RIGHT)
            return ACTION_TURN_RIGHT

        elif turn == 3:
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            self.update_score(ACTION_TURN_LEFT)
            return ACTION_TURN_LEFT

        else:
            self.state.last_action = ACTION_FORWARD
            self.update_score(ACTION_FORWARD)
            self.route.pop(0)
            return ACTION_FORWARD

    def get_result_grid(self):
        return "{}x{}".format(self.state.world_width, self.state.world_height)

    def report_result(self, status):
        if self.result_reported:
            return

        self.result_reported = True
        self.result_data = {
            "algorithm": self.search_algorithm,
            "grid": self.get_result_grid(),
            "steps": self.steps,
            "nodes_explored": self.nodes_explored,
            "score": self.score,
        }
        self.log("===== RESULT =====")
        self.log("Algorithm: {}".format(self.result_data["algorithm"]))
        self.log("Grid: {}".format(self.result_data["grid"]))
        self.log("Steps: {}".format(self.result_data["steps"]))
        self.log("Nodes explored: {}".format(self.result_data["nodes_explored"]))
        self.log("Score: {}".format(self.result_data["score"]))
        print("Algorithm:", self.result_data["algorithm"])
        print("Grid:", self.result_data["grid"])
        print("Steps:", self.result_data["steps"])
        print("Nodes explored:", self.result_data["nodes_explored"])
        print("Score:", self.result_data["score"])

    def execute(self, percept):
        ###########################
        # DO NOT MODIFY THIS CODE #
        ###########################

        bump = percept.attributes["bump"]
        dirt = percept.attributes["dirt"]
        home = percept.attributes["home"]

        # Move agent to a randomly chosen initial position
        if self.initial_random_actions > 0:
            self.log("Moving to random start position ({} steps left)".format(self.initial_random_actions))
            return self.move_to_random_start_position(bump)

        # Finalize randomization by properly updating position (without subsequently changing it)
        elif self.initial_random_actions == 0:
            self.initial_random_actions -= 1
            self.state.update_position(bump)
            self.state.last_action = ACTION_SUCK
            self.log("Processing percepts after position randomization")
            return ACTION_SUCK


        ########################
        # START MODIFYING HERE #
        ########################
        self.steps += 1
        # Max iterations for the agent
        if self.iteration_counter < 1:
            if self.iteration_counter == 0:
                self.iteration_counter -= 1
                self.log("Iteration counter is now 0. Halting!")
                self.log("Performance: {}".format(self.performance))
                self.update_score(ACTION_NOP)
                self.report_result("Stopped: iteration limit reached")
            return ACTION_NOP

        self.log("Position: ({}, {})\t\tDirection: {}".format(self.state.pos_x, self.state.pos_y,
                                                              direction_to_string(self.state.direction)))

        self.iteration_counter -= 1
        # Track position of agent
        self.state.update_position(bump)
        if bump:
            # Get an xy-offset pair based on where the agent is facing
            offset = [(0, -1), (1, 0), (0, 1), (-1, 0)][self.state.direction]

            # Mark the tile at the offset from the agent as a wall (since the agent bumped into it)
            self.state.update_world(self.state.pos_x + offset[0], self.state.pos_y + offset[1], AGENT_STATE_WALL)

        # Update perceived state of current tile
        if dirt:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_DIRT)
        else:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_CLEAR)
        # Debug
        self.state.print_world_debug()

        # Save home position
        if home:
            self.home_pos = (self.state.pos_x, self.state.pos_y)

        # Decide action
        # ---- CLEAN ----
        if dirt:
            self.log("DIRT -> SUCK")
            self.state.last_action = ACTION_SUCK
            self.cleaned += 1
            self.update_score(ACTION_SUCK)
            return ACTION_SUCK

        # ---- PLAN ----
        if not self.route:
            # explore unknown first
            if self.search_algorithm == "BFS":
                self.bfs(return_home=False)
            else:
                self.astar(return_home=False)
            # if no unknown → return home
            if not self.route:
                if (self.state.pos_x, self.state.pos_y) == self.home_pos:
                    self.log("FINISHED: cleaned entire map and returned home")
                    self.state.print_world_debug()
                    self.update_score(ACTION_NOP, shutdown=True)
                    self.report_result("Finished")
                    return ACTION_NOP

                self.log("Returning home...")
                if self.search_algorithm == "BFS":
                    self.bfs(return_home=True)
                else:
                    self.astar(return_home=True)

        # ---- EXECUTE PLAN ----
        if self.route:
            return self.move_to(self.route[0])

        if self.terminated:
            self.report_result("Finished")
            return ACTION_NOP
