const express = require("express");
const { PeerServer } = require("peer");
const cors = require("cors");
const https = require("https");
const fs = require("fs");

// Load SSL certificates (ensure you have these files at the correct paths)
const privateKey = fs.readFileSync("private.key", "utf8");
const certificate = fs.readFileSync("server.crt", "utf8");
const ca = fs.readFileSync("server.csr", "utf8"); // Use CA file if needed

const app = express();
const peerPort = 9000; // PeerJS server port
const apiPort = 9001; // Express API port

const peerIp = "192.168.0.162"; // IP address of the machine, or '0.0.0.0' for all interfaces

// Create HTTPS server
const httpsServer = https.createServer(
  { key: privateKey, cert: certificate, ca: ca },
  app
);

// CORS middleware configuration for Express server (Allow all origins for testing)
app.use(
  cors({
    origin: "*", // Allow all origins
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type"],
  })
);

app.use(express.json());

// Create a new PeerJS server instance with CORS enabled
const peerServer = PeerServer({
  port: peerPort,
  host: peerIp,
  path: "/myapp",
  proxied: true,
  cors: {
    origin: "*", // Allow all origins for PeerJS
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type"],
  },
  ssl: {
    key: privateKey,
    cert: certificate,
  },
});

let connectedClients = []; // List to track connected clients
let disconnectedClients = []; // List to track disconnected clients
let pairedClients = []; // List to track paired clients
let pairings = {}; // Map to track pairs of clients
let clientConnections = {}; // Store PeerJS connection objects for active clients

// Log when the PeerJS server is running
peerServer.on("listening", () => {
  console.log(`PeerJS server running on https://${peerIp}:${peerPort}`);
});

// Handle new connections to PeerJS server
peerServer.on("connection", (client) => {
  console.log("New client connected:", client.id);
  console.log("Current pairings:", pairings);

  // Ensure the client is fully connected (check for open connection)
  if (!client.open) {
    console.log(`Client ${client.id} is not fully connected yet.`);
    connectedClients.push(client.id);
    console.log(`Client ${client.id} added to connected clients.`);
    return; // Return if the client is not fully connected
  }

  // Check if the client is already paired with another
  for (let peerId in pairings) {
    if (pairings[peerId].includes(client.id)) {
      // This client is already paired with someone, deny new connections
      console.log(
        `Client ${client.id} is already paired with ${peerId}. Denying new connections.`
      );
      // Remove from connected clients list
      const index = connectedClients.indexOf(client.id);
      if (index > -1) {
        connectedClients.splice(index, 1);
      }
      return;
    }
  }

  // Remove from disconnected clients list if previously disconnected
  const disconnectedIndex = disconnectedClients.indexOf(client.id);
  if (disconnectedIndex > -1) {
    disconnectedClients.splice(disconnectedIndex, 1);
  }

  // Store the connection object for later use
  clientConnections[client.id] = client;

  // Attempt to pair clients if there are at least two connected clients
  if (connectedClients.length >= 2) {
    // Get the last two connected clients for pairing
    const client1 = connectedClients.pop(); // Get the last connected client
    const client2 = connectedClients.pop(); // Get the second last connected client

    // Pair them together if they are both fully connected
    if (isClientConnected(client1) && isClientConnected(client2)) {
      pairPeers(client1, client2);
    } else {
      console.log(
        `Cannot pair ${client1} and ${client2} because one or both are not fully connected.`
      );
      // Re-add the clients to connectedClients if pairing fails
      connectedClients.push(client1);
      connectedClients.push(client2);
    }
  }
});

// Function to check if a client is fully connected
const isClientConnected = (clientId) => {
  const connection = clientConnections[clientId];
  return connection && connection.open;
};

// Function to pair two clients
const pairPeers = (client1, client2) => {
  // Ensure neither client is already paired with someone else
  if (!pairings[client1] && !pairings[client2]) {
    pairings[client1] = [client2];
    pairings[client2] = [client1];
    console.log(`Paired ${client1} with ${client2}`);
    // Track the clients as paired
    pairedClients.push(client1);
    pairedClients.push(client2);
  } else {
    console.log(
      `One or both peers are already paired, cannot pair them again.`
    );
  }
};

// Handle disconnections from PeerJS server
peerServer.on("disconnect", (client) => {
  console.log("Client disconnected:", client.id);

  // Remove client from connectedClients list
  const connectedIndex = connectedClients.indexOf(client.id);
  if (connectedIndex > -1) {
    connectedClients.splice(connectedIndex, 1);
  }

  // Remove client from pairings (if they were paired)
  for (let peerId in pairings) {
    const index = pairings[peerId].indexOf(client.id);
    if (index > -1) {
      pairings[peerId].splice(index, 1);
      if (pairings[peerId].length === 0) {
        delete pairings[peerId]; // Remove the pair if it's empty
      }
    }
  }

  // Add client to disconnectedClients list
  disconnectedClients.push(client.id);
});

// Endpoint to get the list of connected and disconnected clients
app.get("/api/connections", (req, res) => {
  // Filter out clients who are part of a pairing
  const availableClients = connectedClients.filter((clientId) => {
    return !Object.values(pairings).some((pair) => pair.includes(clientId));
  });

  res.json({ connectedClients: availableClients, disconnectedClients });
});

app.post("/api/peerid", (req, res) => {
  const { peerId } = req.body;

  if (!peerId) {
    return res.status(400).json({ message: "peerId is required" });
  }

  console.log("Received peerId:", req.body);
  connectedClients.pop(req.body?._peerId);
  connectedClients.pop(req.body?.peerId);

  pairedClients.push(req.body);

  return res.status(200).json({ message: "successfully connected ", peerId });
});

app.post("/api/peerid-disconnect", (req, res) => {
  const { peerId, _peerId } = req.body;

  if (!peerId) {
    return res.status(400).json({ message: "peerId is required" });
  }

  console.log("Received peerId:", req.body);

  if (
    _peerId &&
    pairedClients.some(
      (client) => client._peerId === _peerId && client.peerId === peerId
    )
  ) {
    pairedClients = pairedClients.filter(
      (client) => !(client._peerId === _peerId && client.peerId === peerId)
    );
  }

  if (!connectedClients.includes(_peerId)) {
    connectedClients.push(_peerId);
  }

  if (!connectedClients.includes(peerId)) {
    connectedClients.push(peerId);
  }

  pairedClients.push(req.body);

  res
    .status(200)
    .json({ message: "Peer disconnected and re-paired successfully." });
});

// Start the HTTPS server for API (Express)
httpsServer.listen(apiPort, "0.0.0.0", () => {
  console.log(`Express API server running on https://192.168.0.162:${apiPort}`);
});

// Periodic logging of connected and disconnected clients every 10 seconds
setInterval(() => {
  console.log("Connected Clients:", connectedClients);
  console.log("Disconnected Clients:", disconnectedClients);
}, 10000); // Log every 10 seconds

// Graceful shutdown: Handle server termination
const shutdown = () => {
  console.log("Shutting down gracefully...");
  peerServer.close(() => {
    console.log("PeerJS server has been shut down.");
  });
  httpsServer.close(() => {
    console.log("Express server has been shut down.");
    process.exit(0);
  });
};

// Catch termination signals (e.g., SIGINT from Ctrl+C)
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

module.exports = { pairPeers }; // Export to allow pairing externally if needed