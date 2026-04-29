#include "astar.h"
#include "utils.h"
#include <queue>
#include <iostream>
#include <algorithm>
using namespace std;

typedef pair<double,int> pii;

void astar(Graph &g, int src, int dest, double congestion, map<int,string> &names) {

    vector<double> gCost(g.V, 1e9);
    vector<int> parent(g.V, -1);
    priority_queue<pii, vector<pii>, greater<pii>> pq;

    gCost[src] = 0;
    pq.push(make_pair(0, src));

    int nodes = 0;

    while(!pq.empty()) {
        pair<double,int> p = pq.top(); pq.pop();
        double fCost = p.first;
        int u = p.second;

        // Ignore stale queue entries that are no longer optimal.
        if (fCost > gCost[u] + heuristic(u, dest)) continue;
        nodes++;

        if(u == dest) break;

        for(auto &e : g.adj[u]) {
            double newG = gCost[u] + e.distance + congestion;
            double newF = newG + heuristic(e.to, dest);

            if(newG < gCost[e.to]) {
                gCost[e.to] = newG;
                parent[e.to] = u;
                pq.push(make_pair(newF, e.to));
            }
        }
    }

    cout << "\n[A*]\n";
    if (gCost[dest] >= 1e9) {
        cout << "No path found." << endl;
        cout << "Nodes explored: " << nodes << endl;
        return;
    }
    cout << "Cost: " << gCost[dest] << endl;
    cout << "Nodes explored: " << nodes << endl;

    // Print path
    vector<int> path;
    int cur = dest;
    while(cur != -1) {
        path.push_back(cur);
        cur = parent[cur];
    }
    reverse(path.begin(), path.end());

    cout << "Path: ";
    for(int i = 0; i < (int)path.size(); i++) {
        cout << names[path[i]];
        if(i != (int)path.size() - 1) cout << " -> ";
    }
    cout << endl;
}