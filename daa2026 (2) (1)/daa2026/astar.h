#ifndef ASTAR_H
#define ASTAR_H

#include "graph.h"
#include <map>
#include <string>

using namespace std;

void astar(Graph &g, int src, int dest, double congestion, map<int,string> &names);

#endif