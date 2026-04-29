#include "graph.h"

Graph::Graph(int V) {
    this->V = V;
    adj.resize(V);
}

void Graph::addEdge(int u, int v, double dist) {
    adj[u].push_back({v, dist});
    adj[v].push_back({u, dist});
}