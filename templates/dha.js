// Initialize the map
var map = L.map('map').setView([12.9716, 77.5946], 13); // Default location coordinates and zoom level

// Set up the OpenStreetMap layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Marker to represent the vehicle location
var vehicleMarker = L.marker([12.9716, 77.5946]).addTo(map); 

// Function to update vehicle location on the map
function updateVehicleLocation(lat, long) {
    vehicleMarker.setLatLng([lat, long]); // Update marker location
    map.setView([lat, long], 13);         // Center the map to the new location
    document.getElementById('vehicleLocation').innerText = `Lat: ${lat.toFixed(4)}, Long: ${long.toFixed(4)}`;
}

// Connect to the backend server with Socket.IO
const socket = io.connect('http://localhost:5000'); // Replace with the actual server URL if different

// Listen for drowsiness updates from the server
socket.on('drowsiness_update', function(data) {
    // Update drowsiness detection information on the webpage
    document.getElementById('eyeStatus').innerText = data.eye_status;
    document.getElementById('drowsinessLevel').innerText = data.drowsiness_level;
    document.getElementById('drowsinessAlertMessage').innerText = data.alert;
    document.getElementById('drowsinessAlertMessage').style.color = data.alert === "Alert!" ? "red" : "green";
});

// Listen for blind spot updates from the server
socket.on('blindspot_update', function(data) {
    document.getElementById('blindSpotDetection').innerText = data.blind_spot_status;
});

// Listen for location updates from the server
socket.on('location_update', function(data) {
    updateVehicleLocation(data.latitude, data.longitude);
    document.getElementById('vehicleSpeed').innerText = `${data.speed} km/h`;
});
