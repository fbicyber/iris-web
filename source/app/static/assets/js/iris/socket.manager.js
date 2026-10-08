/**
 * Socket.IO Connection Manager
 * Provides a single shared socket connection for all modules to prevent
 * connection exhaustion and improve performance.
 */
var SocketManager = (function() {
    var instance = null;
    var namespaces = {};

    function SocketManager() {
        // Single base connection with WebSocket upgrade prioritized
        this.baseSocket = io({
            transports: ['websocket', 'polling'],  // Try WebSocket first
            upgrade: true,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 5
        });

        console.log('[SocketManager] Base connection created');

        // Debug connection state
        this.baseSocket.on('connect', function() {
            console.log('[SocketManager] Connected via', this.baseSocket.io.engine.transport.name);
        }.bind(this));

        this.baseSocket.on('upgrade', function(transport) {
            console.log('[SocketManager] Upgraded to', transport.name);
        });

        this.baseSocket.on('disconnect', function(reason) {
            console.log('[SocketManager] Disconnected:', reason);
        });

        this.baseSocket.on('error', function(error) {
            console.error('[SocketManager] Error:', error);
        });
    }

    /**
     * Get the base socket connection (default namespace)
     */
    SocketManager.prototype.getSocket = function() {
        return this.baseSocket;
    };

    /**
     * Get or create a namespaced socket connection
     * @param {string} namespace - The namespace (e.g., '/alerts', '/server-updates')
     */
    SocketManager.prototype.getNamespace = function(namespace) {
        if (!namespace || namespace === '/') {
            return this.baseSocket;
        }

        if (!namespaces[namespace]) {
            console.log('[SocketManager] Creating namespace connection:', namespace);
            namespaces[namespace] = io(namespace, {
                transports: ['websocket', 'polling'],
                upgrade: true,
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: 5
            });
        }

        return namespaces[namespace];
    };

    /**
     * Disconnect all sockets (cleanup)
     */
    SocketManager.prototype.disconnectAll = function() {
        console.log('[SocketManager] Disconnecting all sockets');

        if (this.baseSocket) {
            this.baseSocket.disconnect();
        }

        Object.keys(namespaces).forEach(function(ns) {
            if (namespaces[ns]) {
                namespaces[ns].disconnect();
            }
        });

        namespaces = {};
    };

    return {
        getInstance: function() {
            if (!instance) {
                instance = new SocketManager();
            }
            return instance;
        }
    };
})();

// Make the manager globally available
window.socketManager = SocketManager.getInstance();
