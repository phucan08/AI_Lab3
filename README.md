# AI_Lab3

How to compile and run the code

Quick Start:
``
cd d:\Artificial Intelligent\Lab\NguyenPhucAn_ITCSIU24001_Lab3\Lab3
python run_lab2.py
``

What You Need:
 - Python 3.x installed
Required packages:
 - tkinter (usually comes with Python)
 - Standard library modules: collections, random, heapq

Full Steps:
1. Open PowerShell in your project directory:
``cd "d:\Artificial Intelligent\Lab\NguyenPhucAn_ITCSIU24001_Lab3\Lab3"``
2. Verify Python is installed:
``python --version``
3. Run the program:
``python run_lab2.py``

What Will Happen:
 - A GUI window opens with the vacuum environment
 - Select an agent type (BFS, A*, Random, or Reactive)
 - Click buttons to run the simulation
 - View logs in the text panel
 - See results with steps, nodes explored, and score

Alternative: Run from VS Code:
Press Ctrl+F5 to run the file, or right-click run_lab2.py → "Run Python File"

Algorithm: Breadth-First Search (BFS) and A*

How the Vacuum Moves

BFS Movement Flow:
 - Explores uniformly in all directions (up, right, down, left)
 - Expands level-by-level - explores all neighbors at distance 1, then distance 2, etc.
 - Finds target by exhaustive search - traces back path once target is found
 - Example: To reach a cell 5 steps away, it might explore ~20+ cells unnecessarily

A* Movement Flow:
 - Prioritizes direction toward goal - uses heuristic to guide search
 - Expands in smart order - focuses on cells closer to target first
 - Still explores alternatives but eliminates obviously longer paths
 - Example: To reach the same cell, might explore only ~8-10 cells by targeting the right direction

In the Code:
 - BFS : Uses deque, explores all neighbors uniformly
 - A* : Uses heapq with f_score = g_score + Manhattan distance heuristic

The agent executes plans using myvacuumagent.py:238-273, which follows the calculated route by rotating and moving forward one step at a time.

Result: A* typically explores significantly fewer nodes while finding equally short paths, making it more efficient for larger grids.





