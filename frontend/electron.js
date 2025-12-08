/**
 * Electron Main Process Entry Point
 * Este arquivo é o ponto de entrada do Electron (substitui background.js para Vite)
 */
const { app, protocol, BrowserWindow } = require('electron')
const path = require('path')
const isDev = process.env.NODE_ENV === 'development'

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
      preload: path.join(__dirname, 'src/preload.js')
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

  // Carregar URL
  if (isDev) {
    // Modo desenvolvimento: conectar ao Vite dev server
    await win.loadURL('http://localhost:5173')
    // Abrir DevTools em desenvolvimento
    win.webContents.openDevTools()
  } else {
    // Modo produção: carregar arquivo local
    await win.loadFile(path.join(__dirname, 'dist/index.html'))
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
  const apiUrl = process.env.VUE_APP_API_URL || process.env.VITE_API_URL || 'https://api.sne-radar.com'
  
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
        // Em desenvolvimento, não mostrar erro (pode ser local)
        if (!${isDev}) {
          alert('⚠️ Não foi possível conectar com o servidor. Verifique sua conexão com a internet.');
        }
        return false;
      }
    })()
  `).catch(err => {
    console.error('Erro ao verificar API:', err)
  })
}

// Este método será chamado quando Electron terminar de inicializar
app.on('ready', async () => {
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
    const apiUrl = process.env.VUE_APP_API_URL || process.env.VITE_API_URL || 'https://api.sne-radar.com'
    if (navigationUrl.startsWith(apiUrl)) {
      // Abrir em navegador externo
      require('electron').shell.openExternal(navigationUrl)
    }
  })
})


