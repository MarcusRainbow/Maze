# Maze
Although Dijkstra's work on mazes is very interesting, his algorithm essentially assumes that the solver has unlimited visibility of the maze. Real mazes are not like that. The person, or rat, walking round the maze initially sees a number of identical corridors stretching away in different directions. She chooses a corridor and walks to the next junction, where there is again some number (perhaps different) of identical corridors. There is no way of identifying corridors or junctions, and she just staggers from junction to junction until she emerges into the sunlight.

A well-behaved maze always has a return path, and the return path is achieved by going back the way you came. Less well-behaved mazes may not always allow you to return the way you came, or may take you somewhere different if you do. This framework allows both well and poorly-behaved mazes.

The exits from each junction may be thought of as existing in two or more dimensions. However, you cannot assume that paths do not cross each other, and there may not be junctions where they do.

A repeating sequence of junctions may indicate that you are in a loop, or it may just mean that you are in a long sequence of repeating junctions, which will eventually do something different, or enter a real loop.
