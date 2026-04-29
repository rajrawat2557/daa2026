#include "astar.h"
#include "utils.h"
#include <queue>
#include <iostream>
using namespace std;

typedef pair<double,int> pii;

void astar(Graph &g, int src, int dest, double congestion) {

    vector<double> gCost(g.V, 1e9);
    priority_queue<pii, vector<pii>, greater<pii>> pq;

    gCost[src] = 0;
    pq.push(make_pair(0, src));

    int nodes = 0;

    while(!pq.empty()) {
        pair<double,int> p = pq.top(); pq.pop();
        double f = p.first;
        int u = p.second;
        nodes++;

        if(u == dest) break;

        for(auto &e : g.adj[u]) {
            double newG = gCost[u] + e.distance + congestion;
            double newF = newG + heuristic(e.to, dest);

            if(newG < gCost[e.to]) {
                gCost[e.to] = newG;
                pq.push(make_pair(newF, e.to));
            }
        }
    }

    cout << "\n[A*]\n";
    cout << "Cost: " << gCost[dest] << endl;
    cout << "Nodes explored: " << nodes << endl;
}