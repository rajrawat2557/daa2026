#include <iostream>
#include <map>
#include <cstdlib>
#include <fstream>
#include "graph.h"
#include "dijkstra.h"
#include "astar.h"
#include "utils.h"
using namespace std;
int main(int a, char* argv[]) {
    Graph g(6);
    map<int, string> names;
    names[0] = "ISBT";
    names[1] = "Clock Tower";
    names[2] = "Rajpur Road";
    names[3] = "Ballupur";
    names[4] = "Prem Nagar";
    names[5] = "Clement Town";
    int src, dest;
    string time;
    double congestion = -1.0;
    bool fromArgs = false;
    if (a >= 4) {
        src = atoi(argv[1]);
        dest = atoi(argv[2]);
        congestion = atof(argv[3]);
        fromArgs = true;
    }
    bool loaded = false;
    if (a >= 5) {
        ifstream fin(argv[4]);
        if (fin.is_open()) {
            int V, E;
            fin >> V >> E;
            if (V > 0 && E >= 0) {
                g = Graph(V);
                for (int i = 0; i < E; i++) {
                int u, v;
                double d;
                fin >> u >> v >> d;
                if (u >= 0 && v >= 0 && u < V && v < V) {
                g.addEdge(u, v, d);
                }
                }
                loaded = true;
            }
        }
    }

    if (!loaded) {
        // Fallback: static roads (distance in km approx)
        g.addEdge(0,1,3); // ISBT → Clock Tower
        g.addEdge(1,2,4); // Clock Tower → Rajpur Road
        g.addEdge(1,3,2); // Clock Tower → Ballupur
        g.addEdge(3,4,5); // Ballupur → Prem Nagar
        g.addEdge(4,5,3); // Prem Nagar → Clement Town
        g.addEdge(2,3,3); // Rajpur Road → Ballupur
    }

    cout << "Locations:\n";
    for(auto &p : names) {
        cout << p.first << " ->" << p.second << endl;
    }

    if (!fromArgs) {
        cout << "\nEnter source (number): ";
        cin >> src;

        cout << "Enter destination (number): ";
        cin >> dest;

        cout << "Enter time (morning/afternoon/night): ";
        cin >> time;
        congestion = getCongestion(time);
    }

    if (src < 0 || src >= g.V || dest < 0 || dest >= g.V) {
        cout << "Invalid source/destination index. Please choose numbers shown in the list." << endl;
        return 1;
    }
    if (congestion < 0) {
        cout << "Invalid congestion value. It must be >= 0." << endl;
        return 1;
    }
    cout << "\nSource: " << names[src];
    cout << "\nDestination: " << names[dest] << endl;
    cout << "\nCongestion used: " << congestion << endl;
    cout << "Graph data: " << (loaded ? "Mappls-derived edges" : "Static fallback edges") << endl;
    dijkstra(g, src, dest, congestion,names);
    astar(g, src, dest, congestion,names);
    return 0;
}