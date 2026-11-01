(()=>{
const modeKey='pocket-local-account-mode',feedback=document.getElementById('localFeedback');
function applyMode(){let mode='1';try{mode=localStorage.getItem(modeKey)||'1';}catch{}document.body.dataset.accounts=mode;document.getElementById('accountMode').value=mode;}
const initialMode=location.hash.match(/^#accounts=([12])$/)?.[1];if(initialMode){try{localStorage.setItem(modeKey,initialMode);history.replaceState(null,'',location.href.split('#')[0]);}catch{}}
applyMode();document.getElementById('accountMode').onchange=e=>{try{localStorage.setItem(modeKey,e.target.value);applyMode();}catch{feedback.textContent='Tarayıcı kayıt alanı kapalı.';}};
async function request(path,body){const r=await fetch('/api/pokemon/'+path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined});const d=await r.json();if(!r.ok)throw Error(d.error||'Kayıt başarısız.');return d;}
document.getElementById('cards').addEventListener('change',async e=>{
 const input=e.target;if(!input.matches('[data-count-account]'))return;
 const count=Number(input.value);if(!input.value.trim()||!Number.isInteger(count)||count<0||count>999999){input.setCustomValidity('0–999999 arası tam sayı gir.');input.reportValidity();return;}input.setCustomValidity('');input.disabled=true;
 try{const state=await request('quantity',{account:input.dataset.countAccount,key:input.dataset.key,count});acceptShared(state);}
 catch(error){feedback.textContent=error.message;alert(error.message);}finally{input.disabled=false;}
});
document.getElementById('backupLocal').onclick=async()=>{try{const d=await request('backup'),url=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='pocket-koleksiyon-yedegi.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);feedback.textContent='Yedek indirildi. Hesap bağlantıları ve yetki anahtarları bu dosyaya eklenmez.';}catch(e){feedback.textContent=e.message;}};
document.getElementById('restoreLocal').onchange=async e=>{
 const file=e.target.files[0];if(!file)return;
 try{if(file.size>3*1024*1024)throw Error('Yedek 3 MB sınırını aşıyor.');const data=JSON.parse(await file.text());PocketLocal.validate(data);if(!confirm('Bu yedek mevcut yerel koleksiyonun yerini alacak. Kayıtlı takas planı yeniden oluşturulacak. Önce mevcut verilerini yedeklediğinden emin ol. Devam edilsin mi?'))return;const state=await request('restore',data);acceptShared(state);feedback.textContent='Yedek yüklendi. Takas taslağı ve bakiyeler alındı; planı yeniden onaylayabilirsin. Aktarım kullanıyorsan hesap bağlantılarını yeniden ekle.';}catch(error){feedback.textContent=error.message;}finally{e.target.value='';}
};

// File URLs may have separate storage areas. Keep trade in a child view and relay its API to this collection.
if(location.protocol==='file:'){
 let tradeDialog,frame;
 document.getElementById('tradePlanOpen').addEventListener('click',e=>{
  e.preventDefault();if(!tradeDialog){tradeDialog=document.createElement('dialog');tradeDialog.className='local-trade-dialog';tradeDialog.setAttribute('aria-label','Trade planı');frame=document.createElement('iframe');frame.title='Trade planı';frame.src='pokemon-trade.html';tradeDialog.append(frame);document.body.append(tradeDialog);}tradeDialog.showModal();
 });
 window.addEventListener('message',e=>{
  if(!frame||e.source!==frame.contentWindow)return;
  if(e.data?.type==='pocket-close-trade'){tradeDialog.close();pullShared();return;}
  if(e.data?.type!=='pocket-request')return;
  try{const data=PocketLocal.handleRequest(e.data.path,e.data.body);e.source.postMessage({type:'pocket-response',id:e.data.id,status:200,data},'*');}
  catch(error){e.source.postMessage({type:'pocket-response',id:e.data.id,status:400,data:{error:error.message}},'*');}
 });
}

// Download is a screen snapshot; JSON is the complete portable backup.
document.getElementById('download').title='Tam veri yedeği için JSON yedeğini kullan. HTML kopyası bu klasördeki dosyalara ihtiyaç duyar.';
if(!PocketLocal.bridge){document.getElementById('importSummary').textContent='Başlatıcı ile kullanılabilir';document.getElementById('importGlobalStatus').textContent='Bu sürüm tarayıcıda çalışıyor. Otomatik aktarım için rehberdeki yerel başlatıcıyı kullan. Kayıtlar iki çalışma biçiminde ayrıdır; geçişte JSON yedeği kullan.';}
})();
