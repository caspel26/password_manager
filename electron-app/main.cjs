const { app, BrowserWindow, Menu } = require('electron')
const { screen } = require('electron')

require('electron-reload')(__dirname, {
  electron: require(`${__dirname}/node_modules/electron`),
  watch: ['dist', 'src']
});


let win
app.whenReady().then(() => {
  const primaryDisplay = screen.getPrimaryDisplay()
  const { width, height } = primaryDisplay.workAreaSize

  win = new BrowserWindow({
    width: 400,
    height: 600,
    x: width - 400,
    y: height - 600,
    webPreferences: {
      nodeIntegration: true
    }
  })
  win.loadURL('http://localhost:5173')
  Menu.setApplicationMenu(null)
})
