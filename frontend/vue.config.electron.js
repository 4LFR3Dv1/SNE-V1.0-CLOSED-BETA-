const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  pluginOptions: {
    electronBuilder: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: 'src/preload.js',
      builderOptions: {
        appId: 'com.sne.radar',
        productName: 'SNE Radar',
        copyright: 'Copyright © 2025 SNE Trading Systems',
        directories: {
          output: 'dist_electron',
          buildResources: 'build'
        },
        files: [
          'dist/**/*',
          'node_modules/**/*',
          'package.json'
        ],
        extraResources: [
          {
            from: 'dist',
            to: 'app/dist',
            filter: ['**/*']
          }
        ],
        win: {
          target: [
            {
              target: 'nsis',
              arch: ['x64']
            }
          ],
          icon: 'build/icon.ico'
        },
        mac: {
          target: [
            {
              target: 'dmg',
              arch: ['x64', 'arm64']
            }
          ],
          icon: 'build/icon.icns',
          category: 'public.app-category.finance',
          hardenedRuntime: true,
          gatekeeperAssess: false,
          entitlements: 'build/entitlements.mac.plist',
          entitlementsInherit: 'build/entitlements.mac.plist'
        },
        linux: {
          target: [
            {
              target: 'AppImage',
              arch: ['x64']
            }
          ],
          icon: 'build/icon.png',
          category: 'Finance'
        },
        nsis: {
          oneClick: false,
          allowToChangeInstallationDirectory: true,
          createDesktopShortcut: true,
          createStartMenuShortcut: true,
          shortcutName: 'SNE Radar'
        },
        dmg: {
          contents: [
            {
              x: 410,
              y: 150,
              type: 'link',
              path: '/Applications'
            },
            {
              x: 130,
              y: 150,
              type: 'file'
            }
          ],
          window: {
            width: 540,
            height: 380
          }
        }
      }
    }
  }
})


