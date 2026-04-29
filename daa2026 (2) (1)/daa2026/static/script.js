const nodesData = window.NODES_DATA || {};

// Initialize Map
const map = L.map('map').setView([30.3165, 78.0322], 13); // Centered around Dehradun

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
}).addTo(map);

// Fix potential Leaflet gray screen issue
setTimeout(() => {
    map.invalidateSize();
}, 500);

const markers = {};
let currentPolyline = null;

// Add markers for all nodes
Object.entries(nodesData).forEach(([id, node]) => {
    const [lat, lng] = node.coord.split(',');
    const marker = L.circleMarker([parseFloat(lat), parseFloat(lng)], {
        radius: 6,
        fillColor: "#38bdf8",
        color: "#fff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
    }).addTo(map);
    
    marker.bindTooltip(node.name, { permanent: true, direction: 'right', className: 'node-label' });
    markers[id] = { marker, lat, lng };
});



// Calculate route
document.getElementById('calculate-btn').addEventListener('click', async () => {
    const src = document.getElementById('src').value;
    const dest = document.getElementById('dest').value;

    const btn = document.getElementById('calculate-btn');
    btn.textContent = 'Calculating...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ src, dest })
        });
        
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.error || 'Server error');
        
        updateUI(data);
    } catch (err) {
        alert("Error calculating route: " + err.message);
        console.error(err);
    } finally {
        btn.textContent = 'Calculate Route';
        btn.disabled = false;
    }
});

function updateUI(data) {
    document.getElementById('results').classList.remove('hidden');
    
    // Update Metrics
    const distText = data.distance ? (data.distance / 1000).toFixed(2) + ' km' : 'N/A';
    const timeText = data.duration ? (data.duration / 60).toFixed(1) + ' min' : 'N/A';
    
    document.getElementById('res-distance').textContent = distText;
    document.getElementById('res-time').textContent = timeText;

    const comparisons = data.comparisons || {};
    const dijkstra = comparisons['Dijkstra'] || { path: '-' };
    const astar = comparisons['A*'] || { path: '-' };

    document.getElementById('res-path').textContent = dijkstra.path !== '-' ? dijkstra.path : astar.path;

    // Draw path on map
    if (currentPolyline) {
        map.removeLayer(currentPolyline);
    }

    if (data.route_geometry) {
        currentPolyline = L.geoJSON(data.route_geometry, {
            style: {
                color: '#000000',
                weight: 4,
                opacity: 0.8,
                dashArray: '10, 10',
                lineJoin: 'round'
            }
        }).addTo(map);
        
        map.fitBounds(currentPolyline.getBounds(), { padding: [50, 50] });
    } else if (dijkstra.path && dijkstra.path !== '-') {
        const pathNames = dijkstra.path.split(' -> ');
        const pathCoords = [];
        
        pathNames.forEach(name => {
            const entry = Object.values(nodesData).find(n => n.name === name);
            if (entry) {
                const [lat, lng] = entry.coord.split(',');
                pathCoords.push([parseFloat(lat), parseFloat(lng)]);
            }
        });

        if (pathCoords.length > 0) {
            currentPolyline = L.polyline(pathCoords, {
                color: '#000000',
                weight: 4,
                opacity: 0.8,
                dashArray: '10, 10',
                lineJoin: 'round'
            }).addTo(map);
            
            map.fitBounds(currentPolyline.getBounds(), { padding: [50, 50] });
        }
    }
}

// Custom CSS for Leaflet tooltips to match dark theme
const style = document.createElement('style');
style.innerHTML = `
    .node-label {
        background: transparent;
        border: none;
        box-shadow: none;
        color: #f8fafc;
        font-weight: 600;
        text-shadow: 1px 1px 2px #000, -1px -1px 2px #000;
    }
    .leaflet-tooltip-left.node-label::before, 
    .leaflet-tooltip-right.node-label::before {
        display: none;
    }
`;
document.head.appendChild(style);
