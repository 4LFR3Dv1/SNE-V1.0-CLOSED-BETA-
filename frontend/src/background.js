import { app, protocol, BrowserWindow } from 'electron'
import { createProtocol } from 'vue-cli-plugin-electron-builder/lib'
import installExtension, { VUEJS_DEVTOOLS } from 'electron-devtools-installer'

const isDevelopment = process.env.NODE_ENV !== 'production'

// Scheme deve ser registrado antes do app estar pronto
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true } }
])

async function createWindow() {
  // Criar janela do navegador
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      // Segurança: desabilitar nodeIntegration
      nodeIntegration: false,
      contextIsolation: true,
      // Permitir requisições HTTPS
      webSecurity: true,
      // Preload script
      preload: __dirname + '/preload.js'
    },
    // Visual moderno
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    frame: true,
    backgroundColor: '#1a1a1a',
    show: false // Não mostrar até carregar
  })

  // Mostrar janela quando pronta
  win.once('ready-to-show', () => {
    win.show()
    
    // Verificar conexão com API
    checkAPIConnection(win)
  })

  if (process.env.WEBPACK_DEV_SERVER_URL) {
    // Modo desenvolvimento
    await win.loadURL(process.env.WEBPACK_DEV_SERVER_URL)
    if (!process.env.IS_TEST) win.webContents.openDevTools()
  } else {
    // Modo produção
    createProtocol('app')
    win.loadURL('app://./index.html')
  }

  // Fechar todas as janelas quando fechar a principal (exceto macOS)
  win.on('closed', () => {
    if (process.platform !== 'darwin') {
      app.quit()
    }
  })
}

/**
 * Verifica conexão com API Cloud
 */
function checkAPIConnection(win) {
  const apiUrl = process.env.VUE_APP_API_URL || 'https://api.sne-radar.com'
  
  win.webContents.executeJavaScript(`
    (async () => {
      try {
        const response = await fetch('${apiUrl}/api/v1/health');
        const data = await response.json();
        
        if (data.status === 'ok') {
          console.log('✅ API conectada:', data);
          return true;
        } else {
          console.error('❌ API retornou status inválido:', data);
          return false;
        }
      } catch (error) {
        console.error('❌ Erro ao conectar com API:', error);
        // Mostrar aviso ao usuário
        alert('⚠️ Não foi possível conectar com o servidor. Verifique sua conexão com a internet.');
        return false;
      }
    })()
  `).catch(err => {
    console.error('Erro ao verificar API:', err)
  })
}

// Este método será chamado quando Electron terminar de inicializar
app.on('ready', async () => {
  if (isDevelopment && !process.env.IS_TEST) {
    // Instalar Vue Devtools
    try {
      await installExtension(VUEJS_DEVTOOLS)
    } catch (e) {
      console.error('Vue Devtools failed to install:', e.toString())
    }
  }
  createWindow()
})

// Sair quando todas as janelas estiverem fechadas
app.on('window-all-closed', () => {
  // No macOS, aplicativos normalmente ficam ativos até o usuário sair explicitamente
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  // No macOS, recriar janela quando o ícone do dock é clicado
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

// Segurança: prevenir navegação para URLs externas
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault()
    // Permitir apenas URLs da API
    if (navigationUrl.startsWith(process.env.VUE_APP_API_URL || 'https://api.sne-radar.com')) {
      // Abrir em navegador externo
      require('electron').shell.openExternal(navigationUrl)
    }
  })
})


