#ifndef GRAPH_H
#define GRAPH_H

#include <vector>
using namespace std;

struct Edge {
    int to;
    double distance;
};

class Graph {
public:
    int V;
    vector<vector<Edge>> adj;

    Graph(int V);
    void addEdge(int u, int v, double dist);
};

#endif