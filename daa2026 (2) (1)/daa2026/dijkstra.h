#ifndef DIJKSTRA_H
#define DIJKSTRA_H

#include "graph.h"
#include <map>
#include <string>

using namespace std;

void dijkstra(Graph &g, int src, int dest, double congestion, map<int,string> &names);

#endif