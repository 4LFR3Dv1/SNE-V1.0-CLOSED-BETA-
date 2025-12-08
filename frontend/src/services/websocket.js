import { io } from 'socket.io-client'

class WebSocketService {
  constructor() {
    this.socket = null
    this.listeners = new Map()
  }

  connect() {
    if (this.socket?.connected) return

    const wsUrl = import.meta.env.VITE_WS_URL || ''
    this.socket = io(wsUrl, {
      path: '/socket.io',
      transports: ['websocket', 'polling']
    })

    this.socket.on('connect', () => {
      console.log('✅ WebSocket conectado')
    })

    this.socket.on('disconnect', () => {
      console.log('❌ WebSocket desconectado')
    })

    // Re-registrar listeners existentes
    this.listeners.forEach((callback, event) => {
      this.socket.on(event, callback)
    })
  }

  on(event, callback) {
    this.listeners.set(event, callback)
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  emit(event, data) {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }
}

export default new WebSocketService()

