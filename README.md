# Maze

Mazes have long been a staple of computer science, from Dijkstra's famous algorithm to early AI experiments in Wumpus World. Most of these experiments, however, assume a rather unrealistic kind of maze. For example, Dijkstra's algorithm requires visibility of the entire maze, Trémaux's requires the ability to make marks on the ends of tunnels, and several require a concept of orientation, and knowledge of the direction of the exit.

Real mazes are not like that. The rat walking round the maze initially sees a number of identical tunnels stretching away in different directions. She chooses a tunnel and walks to the next chamber, which again gives a choice of identical tunnels. There is no way of identifying tunnels, chambers or directions, and she just staggers from junction to junction until she emerges into the sunlight.

Some computer game mazes, such as Zork, are even worse. They have non-bidirectional tunnels, where walking back along the same tunnel takes you somewhere different. We only think about well-behaved mazes, which are properly bidirectional. We also only consider mazes that have at most one tunnel between any two chambers. This makes the mazes roughly the equivalent of bidirectional graphs, in mathematical terms. The difference is that in a maze the order of tunnels around a chamber is important, and fixed.

## Maze solvers

A maze without loops can be solved with a really simple algorithm -- _always turn left_. This is a simple example of a class of algorithm that could be called dead-end elimination. The rat never revisits a dead-end, because the lack of loops means she never revisits anywhere. The always-turn-left method works with our kind of maze, where you cannot recognise chambers or nodes, or make marks.

Where there are loops, the always-turn-left method can lead you into infinite repeats. A simple way to use a _random walk_, by choosing a random direction each time. This works for any maze, and also does not require identification or marks. However, it is really slow for large mazes.

For a maze without many loops, we can improve random walk by adding memory -- _random walk with memory_. If we remember the choices we have made at each chamber, we can know if we are backtracking. We can also maintain a memory of which choices resulted in blind alleys, or chambers where all of the exits were ultimately dead ends. This greatly improves the performance of random walk, because we only ever backtrack in order to check unexplored tunnels that we left behind. This is also a flavour of dead-end elimination.

The classic algorithm for solving a maze which may have loops is _Trémaux's algorithm_, but it requires us to make marks on the tunnels, or equivalently, to identify tunnels, and remember which we have walked along. Trémaux's rat makes a mark at each end of every tunnel she walks along. For example, if she enters and then leaves a dead-end section of the maze, she leaves two marks: one when she enters it and one when she leaves. The rules are:

* If there are tunnels with no marks, choose one of them
* If there are tunnels with one mark, but none with two, choose one of them
* Never enter a tunnel with two marks

Trémaux's algorithm is quite efficient. The two-mark avoidance makes it a dead-end elimination algorithm, while the one-mark avoidance means we thoroughly investigate loops before marking them as dead-ends. However, it is hard to extend Trémaux's algorithm to a rat with memory, because loops simply appear as repeats, with all the tunnels unmarked.

## Cooperative rats

When multiple rats work cooperatively, they can use loop-avoiding dead-end elimination algorithms similar to Trémaux's, even when there are loops. For example, if Alice walks in one direction around a loop, and Bert walks the other (Alice and Bert are common names for rats), when they meet up they can compare the paths they took to get there, and realise that they are in a loop rather than an infinitely-repeating sequence. Of course, Alice may have walked round the loop a few times before she meets Bert coming the other way, so her mental picture of the loop may be larger than the actual loop. However, even this defective picture is much better than no picture, and allows her to deploy dead-end elimination and get to the exit much more quickly than if she had never met Bert, who will also benefit from the meeting.

Cooperative rats are exciting from an AI perpective. It is a simple, well-defined problem, where individuals need quite sophisticated reasoning: the algorithm to merge the memory of two rats is a close friend of the unification algorithm that is the core of Prolog. Moreover, these individuals perform best when in a community of similar individuals. This a simplified version of the life of social animals such as ants, rats or humans. Although it is simpler, it keeps many of the key features, such as the mechanisms behind merging what an individual knows with the knowledge of other individuals and the group.

## Artificial intelligence and artificial life

Early in evolutionary history, plant and animal life diverged. Plants were static, nourishing themselves by photosynthesis, and had no need for intelligence, but animals gradually evolved the ability to move and the intelligence to direct that movement. In all mobile multicelled animals, modules for correlating sensory information with stored maps of the environment are key to their behaviour. Even in animals as simple as bees, the ability to communicate map information with other individuals is a vital part of social interaction. There must therefore be mental modules specialised to the tasks of navigating, adding new information into mental maps, and sharing and integrating maps between individuals.

Higher animals such as humans repurpose these low-level mental modules in metaphorical ways. For example, humans may perceive complex problems as a physical map; computer science discussions use maze and graph metaphors such as Booch and UML diagrams to describe abstract ideas. Thus a possible basis for an intelligent machine is a set of specialised modules for navigating mazes, by painting internal pictures of the maze, communicating those pictures with other instances of the modules, and trying to synthesise an overall picture by merging the pictures.

A machine specialised to computer mazes might then be metaphorically repurposed to solve any sorts of problems that require understanding of a problem space, and communication and merging of partial solutions. Perhaps it is no coincidence that the implementation includes an algorithm that resembles Prolog unification.

## The future

There are still aspects of cooperating rats that have not been solved here. For example, when two rats meet, there can be ambiguity about how their memories can combine. Handling this ambiguity is not unlike linking variables in Prolog unification. Currently, the directions taken by rats are random, apart from avoiding known dead ends. Real world rats might communicate possible future paths -- _you try this path, I'll try that_.

The problem becomes orders of magnitude more complex if some individuals do not cooperate. If the goal is to complete the maze before other individuals, it may be advantageous to lie. An evolutionary algorithm could select for individual rats that succeeded, or perhaps more interesting, genes shared by multiple rats.

Rats in a maze could be a world where genuinely emergent artificial intelligence evolves.
