#include <iostream>
#include <chrono>
#include <map>
#include "graph.h"
#include "dijkstra.h"
#include "astar.h"
#include "utils.h"

using namespace std;
using namespace chrono;

int main() {

    Graph g(6);

    // this is to  Add roads (distance in km approx)
    g.addEdge(0,1,3); // ISBT → Clock Tower
    g.addEdge(1,2,4); // Clock Tower → Rajpur Road
    g.addEdge(1,3,2); // Clock Tower → Ballupur
    g.addEdge(3,4,5); // Ballupur → Prem Nagar
    g.addEdge(4,5,3); // Prem Nagar → Clement Town
    g.addEdge(2,3,3); // Rajpur Road → Ballupur

    // this is for  Map numbers to names
    map<int, string> names;
    names[0] = "ISBT";
    names[1] = "Clock Tower";
    names[2] = "Rajpur Road";
    names[3] = "Ballupur";
    names[4] = "Prem Nagar";
    names[5] = "Clement Town";

    int src, dest;
    string time;

    cout << "Locations:\n";
    for(auto &p : names) {
        cout << p.first << " ->" << p.second << endl;
    }

    cout << "\nEnter source (number): ";
    cin >> src;

    cout << "Enter destination (number): ";
    cin >> dest;

    cout << "Enter time (morning/afternoon/night): ";
    cin >> time;

    double congestion = getCongestion(time);

    cout << "\nSource: " << names[src];
    cout << "\nDestination: " << names[dest] << endl;

    // this is for  Dijkstra
    auto start1 = high_resolution_clock::now();
    dijkstra(g, src, dest, congestion,names);
    auto stop1 = high_resolution_clock::now();

    cout << "Time: "
         << duration_cast<microseconds>(stop1 - start1).count()
         << " microseconds\n";

    // this is  for A*
    auto start2 = high_resolution_clock::now();
    astar(g, src, dest, congestion,names);
    auto stop2 = high_resolution_clock::now();

    cout << "Time: "
         << duration_cast<microseconds>(stop2 - start2).count()
         << " microseconds\n";
    return 0;
}