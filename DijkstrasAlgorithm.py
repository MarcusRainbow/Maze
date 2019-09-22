from Localizer import OneDimensionalLocalizer
from SimpleMaze import random_maze, render_graph
from typing import List, Dict

# Given a maze, and the start and end nodes, return a dictionary of the distances
# from the start to each of the positions in the maze. The end node should always
# be present in the dictionary, but some other nodes may not be, if they did not
# need visiting by the algorithm.
def dijkstra(maze: List[List[int]], start: int, end: int) -> Dict[int, int]:
    
    # 1. Create a set of all unvisited nodes (if the end is not in the set, add that too)
    unvisited = { i for i in range(len(maze)) }
    if end >= len(maze):
        unvisited.add(end)

    # 2. Set a tentative distance for each node (we only know the start node is zero)
    distance = {start: 0}
    current = start

    while current != end:

        # 3. For the current node, consider all of its unvisited neighbours and calculate
        # their tentative distances through the current node. (We assume that all edges
        # have length one.)
        neighbour_distance = distance[current] + 1 
        for neighbour in maze[current]:
            if neighbour in unvisited:
                if (neighbour not in distance) or (distance[neighbour] > neighbour_distance):
                    distance[neighbour] = neighbour_distance
    
        # 4. When we are done considering all of the unvisited neighbours of the current
        # node, mark the current node as visited and remove it from the unvisited set.
        unvisited.remove(current)

        # show where we are and how we are progressing
        A = ord('A')
        print("current=%s" % chr(current + A))
        unvisited_as_str = { chr(v + A) for v in unvisited }
        distance_as_str = { chr(n + A): d for (n, d) in distance.items() }
        print("  unvisited: %s" % unvisited_as_str)
        print("  distance: %s" % distance_as_str)

        # 5. If the destination node has been marked visited, then stop. The algorithm has finished.
        # (This is handled by the condition above -- "while current != end", as the current node is
        # always marked as visited, and the distance of the current node is not changed)

        # 6. Otherwise, select the unvisited node that is marked with the smallest 
        # tentative distance, set it as the new "current node", and go back to step 3.
        INFINITE = 1000000
        smallest_distance = INFINITE
        current = -1
        for next in unvisited:
            if next in distance:
                if distance[next] < smallest_distance:
                    smallest_distance = distance[next]
                    current = next
            elif current == -1:
                current = next

    return distance          

def test_dijkstras_algo():
    SIZE = 25
    maze = random_maze(0.5, OneDimensionalLocalizer(SIZE, 5))
    #print(maze)
    render_graph(maze, "temp/dijkstras_maze")
    distances = dijkstra(maze, 0, SIZE)
    print("test_dijkstras_algo calculated distance to end as %i" % distances[SIZE])
    assert(len(distances) == SIZE + 1)

if __name__ == "__main__":
    test_dijkstras_algo()