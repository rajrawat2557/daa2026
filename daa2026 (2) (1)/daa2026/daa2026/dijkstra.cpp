#include "dijkstra.h"
#include <queue>
#include <iostream>
using namespace std;

typedef pair<double,int> pii;

void dijkstra(Graph &g, int src, int dest, double congestion) {

    vector<double> dist(g.V, 1e9);
    priority_queue<pii, vector<pii>, greater<pii>> pq;

    dist[src] = 0;
    pq.push(make_pair(0, src));

    int nodes = 0;

    while(!pq.empty()) {
        pair<double,int> p = pq.top(); pq.pop();
        double cost = p.first;
        int u = p.second;
        nodes++;

        for(auto &e : g.adj[u]) {
            double newCost = cost + e.distance + congestion;

            if(newCost < dist[e.to]) {
                dist[e.to] = newCost;
                pq.push(make_pair(newCost, e.to));
            }
        }
    }

    cout << "\n[Dijkstra]\n";
    cout << "Cost: " << dist[dest] << endl;
    cout << "Nodes explored: " << nodes << endl;
}