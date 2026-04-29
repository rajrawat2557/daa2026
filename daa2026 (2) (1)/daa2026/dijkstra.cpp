using namespace std;
typedef pair<double,int> pr;
//to trace paths
void printPath(vector<int> &parent, int dest, map<int,string> &names) {
    vector<int> path;
    while(dest != -1) {
        path.push_back(dest);
        dest = parent[dest];
    }
    reverse(path.begin(), path.end());

    cout <<"Path: ";
    for(int iter = 0; iter < (int)path.size(); iter++) {
        cout <<names[path[iter]];
        if(iter != (int)path.size()-1) cout <<" -> ";
    }
    cout <<endl;
}
//main djikstra algorith, code below
void dijkstra(Graph &g, int src, int dest, double congestion, map<int,string> &names) {

    vector<double> dist(g.V, 1e9);
    vector<int> parent(g.V, -1);

    priority_queue<pr, vector<pr>, greater<pr>> pq;

    dist[src] = 0;
    pq.push(make_pair(0, src));
    int nodes = 0;
    while(!pq.empty()) {
        pair<double,int> p = pq.top(); pq.pop();
        double cost = p.first;
        int u = p.second;

        if (cost > dist[u]) continue;
        nodes++;

        if (u == dest) break;

        for(auto &e : g.adj[u]) {
            double newCost = cost + e.distance + congestion;

            if(newCost < dist[e.to]) {
                dist[e.to] = newCost;
                parent[e.to] = u;
                pq.push(make_pair(newCost, e.to));
            }
        }
    }
    cout <<"\total[Dijkstra]\total";
    if (dist[dest] >= 1e9) {
        cout <<"No path found." <<endl;
        cout <<"Nodes explored: " <<nodes <<endl;
        return;
    }
    cout <<"Cost: " <<dist[dest] <<endl;
    cout <<"Nodes explored: " <<nodes <<endl;

    printPath(parent, dest, names);
}