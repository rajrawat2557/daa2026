#include "dijkstra.h"
#include <queue>
#include <iostream>
#include <vector>
using namespace std;

typedef pair<double,int> pii;

void printPath(vector<int> &parent, int dest, map<int,string> &names) {
    vector<int> path;

    while(dest != -1) {
        path.push_back(dest);
        dest = parent[dest];
    }

    reverse(path.begin(), path.end());

    cout << "Path: ";
    for(int i = 0; i < path.size(); i++) {
        cout << names[path[i]];
        if(i != path.size()-1) cout << " -> ";
    }
    cout << endl;
}

void dijkstra(Graph &g, int src, int dest, double congestion, map<int,string> &names) {

    vector<double> dist(g.V, 1e9);
    vector<int> parent(g.V, -1);

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
                parent[e.to] = u;
                pq.push(make_pair(newCost, e.to));
            }
        }
    }

    cout << "\n[Dijkstra]\n";
    cout << "Cost: " << dist[dest] << endl;
    cout << "Nodes explored: " << nodes << endl;

    printPath(parent, dest, names);
}