const express = require('express');
const { PeerServer } = require('peer');
const cors = require('cors');
const http = require('http');

const app = express();
const port = 9000; // PeerJS server port
const port_connections = 9001; // Express API port

const peerIp = '192.168.0.121'; // IP address of the machine

// Create a new PeerJS server instance with CORS enabled
const peerServer = PeerServer({
    port: port,
    host: peerIp,
    path: '/myapp',
    proxied: true,
    cors: {
        origin: ['http://localhost:3000', 'https://192.168.0.121:3000'], // Allowed origins
        methods: ['GET', 'POST', 'OPTIONS'], // Allowed methods
        allowedHeaders: ['Content-Type'], // Allowed headers (if needed)
    },
});

// Enable CORS for your client-side applications (add more origins if needed)
app.use(cors({
    origin: [
      
        'http://192.168.0.100:9001',
        'http://192.168.0.100:9000',
        'http://192.168.0.100:3000',
        'https://192.168.0.121:3000'
    ],
}));

// Log when the PeerJS server is running
peerServer.on('listening', () => {
    console.log('PeerJS server running on port 9000');
});

const connectedClients = ['yfvhdfhtgdhtg'];
const disconnectedClients = [];

// Handle new connections to PeerJS server
peerServer.on('connection', (client) => {
    console.log('New client connected:', client.id);

    // Check if client was previously disconnected
    const disconnectedIndex = disconnectedClients.indexOf(client.id);
    if (disconnectedIndex > -1) {
        disconnectedClients.splice(disconnectedIndex, 1);
    }
    connectedClients.push(client.id);
});

// Handle disconnections from PeerJS server
peerServer.on('disconnect', (client) => {
    console.log('Client disconnected:', client.id);

    // Remove client from the connected clients list
    const connectedIndex = connectedClients.indexOf(client.id);
    if (connectedIndex > -1) {
        connectedClients.splice(connectedIndex, 1);
    }
    disconnectedClients.push(client.id);
});

// Endpoint to get the list of connected and disconnected clients
app.get('/api/connections', (req, res) => {
    res.json({ connectedClients, disconnectedClients });
});

// Start the Express server on port 9001 (for API)
const server = http.createServer(app);
server.listen(port_connections, '192.168.0.121', () => {
    console.log(`Express server running on port ${port_connections}`);
});

// Periodic logging of connected and disconnected clients every 10 seconds
setInterval(() => {
    console.log('Connected Clients:', connectedClients);
    console.log('Disconnected Clients:', disconnectedClients);
}, 10000); // Log every 10 seconds

// Graceful shutdown: Handle server termination
const shutdown = () => {
    console.log('Shutting down gracefully...');
    peerServer.close(() => {
        console.log('PeerJS server has been shut down.');
    });
    server.close(() => {
        console.log('Express server has been shut down.');
        process.exit(0);
    });
};

// Catch termination signals (e.g., SIGINT from Ctrl+C)
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
