/**
 * Preload script - Bridge seguro entre Electron e Vue
 * Expõe APIs seguras para o frontend
 */
const { contextBridge, ipcRenderer } = require('electron')

// Expor APIs seguras para o Vue
contextBridge.exposeInMainWorld('electronAPI', {
  // Versão do app
  getVersion: () => {
    try {
      return require('../../package.json').version
    } catch {
      return '1.0.0'
    }
  },
  
  // Informações do sistema
  getPlatform: () => process.platform,
  
  // Informações do sistema operacional
  getOSInfo: () => {
    return {
      platform: process.platform,
      arch: process.arch,
      version: process.getSystemVersion ? process.getSystemVersion() : 'unknown'
    }
  },
  
  // Eventos (se necessário no futuro)
  on: (channel, callback) => {
    const validChannels = ['app-version', 'update-available']
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, callback)
    }
  },
  
  // Remover listener
  removeListener: (channel, callback) => {
    ipcRenderer.removeListener(channel, callback)
  }
})

// Log para debug
console.log('✅ Preload script carregado')


