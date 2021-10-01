#!/usr/bin/env python3

from heapq import *

def friendship_policy(graph, start, end):
    """Implement Dijktra algorithm to find to shortest path between the two points
    >>> graph = {0:{1:[0,1], 2:[0,2], 3:[0,3]}, 1:{}, 2:{}, 3:{4:[3,4]}, 4:{}}
    >>> friendship_policy(graph, 0, 4)
    ([0, 3], [3, 4])
    >>> graph = {0:{1:[0,1]}, 1:{2:[1,2]}, 2:{3:[2,3], 1:[2,1]}, 3:{4:[3,4]}, 4:{}}
    >>> friendship_policy(graph, 0, 4)
    ([0, 1], [1, 2], [2, 3], [3, 4])
    >>> graph = {0:{1:[0,1]}, 1:{2:[1,2]}, 2:{}, 3:{4:[3,4]}, 4:{1:[4,1]}}
    >>> friendship_policy(graph, 0, 4)
    >>> graph = {0:{1:[0,1]}, 1:{0:[1,0], 2:[1,2], 4:[1,4]}, 2:{3:[2,3]}, 3:{4:[3,4]}, 4:{1:[4,1]}}
    >>> friendship_policy(graph, 0, 4)
    ([0, 1], [1, 4])
    """
    q = [(0, start),]
    heapify(q)
    visited = set()
    min_dist = {start:0}
    min_path = {start:()}

    while q:
        (dist, n0) = heappop(q)
        visited.add(n0)
        for n1 in graph[n0]:
            d = dist + 1
            if n1 not in visited:
                if (n1 not in min_dist) or (d < min_dist[n1]):
                    min_dist[n1] = d
                    min_path[n1] = min_path[n0] + (graph[n0][n1],)
                heappush(q, (min_dist[n1], n1))
    if end in min_path:
        return min_path[end]
    else:
        return []

if __name__ == "__main__":
    import doctest
    exit(doctest.testmod()[0])
