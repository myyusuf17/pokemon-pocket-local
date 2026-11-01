'use strict';
const {app,BrowserWindow,Menu,dialog,shell,session}=require('electron');
const {spawn}=require('node:child_process');
const path=require('node:path');
const crypto=require('node:crypto');
const fs=require('node:fs');
app.setName('Pocket Local');
if(process.env.POCKET_LOCAL_TEST_DATA){fs.mkdirSync(process.env.POCKET_LOCAL_TEST_DATA,{recursive:true});app.setPath('userData',path.resolve(process.env.POCKET_LOCAL_TEST_DATA));}
let backend,window,base,quitting=false;
if(!app.requestSingleInstanceLock())app.quit();
app.on('second-instance',()=>{if(window){if(window.isMinimized())window.restore();window.focus();}});
function stop(){if(backend){backend.kill();backend=null;}}
app.on('before-quit',()=>{quitting=true;stop();});
app.on('window-all-closed',()=>app.quit());
app.whenReady().then(async()=>{
 const resources=app.isPackaged?process.resourcesPath:path.resolve(__dirname,'../.desktop-build');
 const site=path.join(resources,app.isPackaged?'site':'site'),runtime=path.join(resources,'runtime');
 const executable=process.platform==='win32'?path.join(runtime,'python','python.exe'):path.join(runtime,'pocket-backend','pocket-backend');
 const args=process.platform==='win32'?[path.join(site,'server.py')]:[];
 const dataDir=app.getPath('userData');
 fs.mkdirSync(dataDir,{recursive:true,mode:0o700});
 const token=crypto.randomBytes(32).toString('hex');
 let startupBuffer='';
 try{
  base=await new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>reject(Error('Yerel veri servisi başlatılamadı.')),30000);
   backend=spawn(executable,[...args,'--port','0','--no-browser','--data-dir',dataDir],{cwd:site,windowsHide:true,stdio:['ignore','pipe','pipe'],env:{...process.env,POCKET_SITE_ROOT:site,POCKET_DESKTOP_TOKEN:token,PYTHONUNBUFFERED:'1',PYTHONUTF8:'1',PYTHONIOENCODING:'utf-8'}});
   backend.once('error',error=>{clearTimeout(timer);reject(error);});
   backend.stdout.on('data',chunk=>{startupBuffer+=chunk.toString();const match=startupBuffer.match(/Pocket Local: (http:\/\/127\.0\.0\.1:\d+)/);if(match){clearTimeout(timer);resolve(match[1]);}});
   // Never log imported URLs, authorization values or HTTP bodies.
   backend.stderr.on('data',()=>{});
   backend.once('exit',()=>{clearTimeout(timer);if(!base)reject(Error('Yerel veri servisi beklenmedik şekilde kapandı.'));else if(!quitting){dialog.showErrorBox('Pocket Local','Veri servisi kapandı. Uygulamayı yeniden açabilirsin.');app.quit();}});
  });
  session.defaultSession.webRequest.onBeforeSendHeaders((details,callback)=>{
   if(details.url.startsWith(base+'/'))details.requestHeaders['X-Pocket-Desktop-Token']=token;
   callback({requestHeaders:details.requestHeaders});
  });
  session.defaultSession.setPermissionRequestHandler((_webContents,_permission,callback)=>callback(false));
  Menu.setApplicationMenu(Menu.buildFromTemplate([
   {label:'Pocket Local',submenu:[{label:'Veri klasörünü aç',click:()=>shell.openPath(dataDir)},{type:'separator'},{role:'quit',label:'Çıkış'}]},
   {label:'Düzenle',submenu:[{role:'undo'},{role:'redo'},{type:'separator'},{role:'cut'},{role:'copy'},{role:'paste'},{role:'selectAll'}]},
   {label:'Görünüm',submenu:[{role:'resetZoom'},{role:'zoomIn'},{role:'zoomOut'},{role:'togglefullscreen'}]}
  ]));
  window=new BrowserWindow({width:1280,height:850,minWidth:380,minHeight:600,title:'Pocket Local',backgroundColor:'#f7f8fa',show:false,webPreferences:{nodeIntegration:false,contextIsolation:true,sandbox:true,webSecurity:true}});
  window.webContents.setWindowOpenHandler(({url})=>{if(url.startsWith('https://'))shell.openExternal(url);return {action:'deny'};});
  window.webContents.on('will-navigate',(event,url)=>{if(!url.startsWith(base+'/')){event.preventDefault();if(url.startsWith('https://'))shell.openExternal(url);}});
  window.once('ready-to-show',()=>window.show());
  await window.loadURL(base+'/');
 }catch(error){stop();dialog.showErrorBox('Pocket Local açılamadı',error.message);app.quit();}
});
