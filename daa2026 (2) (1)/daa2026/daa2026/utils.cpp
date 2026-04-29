#include "utils.h"
#include <cmath>

double getCongestion(string time) {
    if(time == "morning") return 5;
    if(time == "afternoon") return 3;
    if(time == "night") return 1;
    return 2;
}

double heuristic(int u, int v) {
    return abs(u - v);
}
