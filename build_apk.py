import os,struct,hashlib,zlib,zipfile,subprocess,collections,base64,secrets
from pathlib import Path
ROOT=Path(__file__).parent
OUT=ROOT/'APK_Lab_0.1.apk'
APP='Lcom/apklab/workshop/MainActivity;'; CHROME='Lcom/apklab/workshop/PickerChrome;'
ACT='Landroid/app/Activity;'; WEB='Landroid/webkit/WebView;'; WCH='Landroid/webkit/WebChromeClient;'

# Dalvik assembler used to keep this tiny build entirely offline.
class Code:
 def __init__(self,regs,ins):self.ops=[];self.regs=regs;self.ins=ins
 def emit(self,op,*args):self.ops.append((op,args));return self
 def label(self,name):self.ops.append(('label',(name,)));return self
 def words(self,dex):
  sizes={'label':0,'retvoid':1,'ret':1,'moveobj':1,'const4':1,'goto':2,'new':2,'string':2,'const16':2,'array':2,'iget':2,'iput':2,'ifeqz':2,'ifne':2,'aput':2,'invoke':3}
  loc={};p=0
  for op,arg in self.ops:
   if op=='label':loc[arg[0]]=p
   else:p+=sizes[op]
  result=[];p=0
  for op,arg in self.ops:
   a=arg
   if op=='label':continue
   if op=='retvoid':w=[0x000e]
   elif op=='ret':w=[0x000f|(a[0]<<8)]
   elif op=='moveobj':w=[0x000c|(a[0]<<8)]
   elif op=='const4':
    r,x=a;assert 0<=r<16 and -8<=x<=7;w=[0x12|(r<<8)|((x&15)<<12)]
   elif op=='const16':r,x=a;w=[0x13|(r<<8),x&65535]
   elif op=='new':r,cls=a;w=[0x22|(r<<8),dex.typeid[cls]]
   elif op=='string':r,s=a;w=[0x1a|(r<<8),dex.strid[s]]
   elif op=='array':r,n,cls=a;w=[0x23|(r<<8)|(n<<12),dex.typeid[cls]]
   elif op in ('iget','iput'):
    r1,r2,field=a;w=[(0x54 if op=='iget' else 0x5b)|(r1<<8)|(r2<<12),dex.fieldid[field]]
   elif op=='aput':x,y,z=a;w=[0x4d|(x<<8),y|(z<<8)]
   elif op=='ifeqz':r,lab=a;w=[0x38|(r<<8),(loc[lab]-p)&65535]
   elif op=='ifne':r1,r2,lab=a;w=[0x33|(r1<<8)|(r2<<12),(loc[lab]-p)&65535]
   elif op=='goto':lab=a[0];w=[0x29,(loc[lab]-p)&65535]
   elif op=='invoke':
    kind,regs,method=a;opcode={'virtual':0x6e,'super':0x6f,'direct':0x70,'static':0x71,'interface':0x72}[kind]
    assert len(regs)<=5 and all(x<16 for x in regs)
    pad=list(regs)+[0]*(5-len(regs));C,D,E,F,G=pad
    w=[opcode | (len(regs)<<12)|(G<<8),dex.methodid[method],C|(D<<4)|(E<<8)|(F<<12)]
   else:raise ValueError(op)
   result+=w;p+=len(w)
  return result

def M(cls,name,args,ret):return(cls,name,tuple(args),ret)
def F(cls,name,typ):return(cls,name,typ)
VOID='V'; STRING='Ljava/lang/String;'; BUNDLE='Landroid/os/Bundle;'; INTENT='Landroid/content/Intent;'; VIEW='Landroid/view/View;'; CONTEXT='Landroid/content/Context;'; SETTINGS='Landroid/webkit/WebSettings;'; CALLBACK='Landroid/webkit/ValueCallback;'; CHOOSE='Landroid/webkit/WebChromeClient$FileChooserParams;'; URI='Landroid/net/Uri;'; URIARR='[Landroid/net/Uri;'; OBJ='Ljava/lang/Object;'; BOOL='Z'; INTEGER='I'

c0=Code(1,1).emit('invoke','direct',[0],M(ACT,'<init>',[],VOID)).emit('retvoid')
c1=Code(7,2).emit('invoke','super',[5,6],M(ACT,'onCreate',[BUNDLE],VOID)).emit('new',0,WEB).emit('invoke','direct',[0,5],M(WEB,'<init>',[CONTEXT],VOID)).emit('invoke','virtual',[0],M(WEB,'getSettings',[],SETTINGS)).emit('moveobj',1).emit('const4',2,1).emit('invoke','virtual',[1,2],M(SETTINGS,'setJavaScriptEnabled',[BOOL],VOID)).emit('invoke','virtual',[1,2],M(SETTINGS,'setAllowFileAccess',[BOOL],VOID)).emit('new',3,CHROME).emit('invoke','direct',[3,5],M(CHROME,'<init>',[APP],VOID)).emit('invoke','virtual',[0,3],M(WEB,'setWebChromeClient',[WCH],VOID)).emit('string',4,'file:///android_asset/index.html').emit('invoke','virtual',[0,4],M(WEB,'loadUrl',[STRING],VOID)).emit('invoke','virtual',[5,0],M(ACT,'setContentView',[VIEW],VOID)).emit('retvoid')
c2=Code(9,4).emit('invoke','super',[5,6,7,8],M(ACT,'onActivityResult',[INTEGER,INTEGER,INTENT],VOID)).emit('iget',0,5,F(APP,'callback',CALLBACK)).emit('ifeqz',0,'ret').emit('const4',2,-1).emit('ifne',7,2,'none').emit('ifeqz',8,'none').emit('invoke','virtual',[8],M(INTENT,'getData',[],URI)).emit('moveobj',2).emit('ifeqz',2,'none').emit('const4',3,1).emit('array',3,3,URIARR).emit('const4',4,0).emit('aput',2,3,4).emit('invoke','interface',[0,3],M(CALLBACK,'onReceiveValue',[OBJ],VOID)).emit('goto','clear').label('none').emit('const4',1,0).emit('invoke','interface',[0,1],M(CALLBACK,'onReceiveValue',[OBJ],VOID)).label('clear').emit('const4',1,0).emit('iput',1,5,F(APP,'callback',CALLBACK)).label('ret').emit('retvoid')
c3=Code(2,2).emit('invoke','direct',[0],M(WCH,'<init>',[],VOID)).emit('iput',1,0,F(CHROME,'host',APP)).emit('retvoid')
c4=Code(8,4).emit('iget',0,4,F(CHROME,'host',APP)).emit('iput',6,0,F(APP,'callback',CALLBACK)).emit('new',1,INTENT).emit('string',2,'android.intent.action.OPEN_DOCUMENT').emit('invoke','direct',[1,2],M(INTENT,'<init>',[STRING],VOID)).emit('string',2,'*/*').emit('invoke','virtual',[1,2],M(INTENT,'setType',[STRING],INTENT)).emit('string',2,'android.intent.category.OPENABLE').emit('invoke','virtual',[1,2],M(INTENT,'addCategory',[STRING],INTENT)).emit('const16',3,101).emit('invoke','virtual',[0,1,3],M(ACT,'startActivityForResult',[INTENT,INTEGER],VOID)).emit('const4',0,1).emit('ret',0)

classes={APP:{'parent':ACT,'fields':[('callback',CALLBACK,1)],'methods':[('<init>',(),VOID,1,c0),('onCreate',(BUNDLE,),VOID,4,c1),('onActivityResult',(INTEGER,INTEGER,INTENT),VOID,4,c2)]},CHROME:{'parent':WCH,'fields':[('host',APP,2)],'methods':[('<init>',(APP,),VOID,1,c3),('onShowFileChooser',(WEB,CALLBACK,CHOOSE),BOOL,1,c4)]}}

def uleb(n):
 out=bytearray()
 while True:
  b=n&0x7f;n>>=7;out.append(b|128 if n else b)
  if not n:return bytes(out)

def align(buf,n=4):buf.extend(b'\x00'*(-len(buf)%n))

class Dex:
 def __init__(self):
  allmethod=set();allfield=set();types=set();strings=set()
  for cls,inf in classes.items():
   types.update([cls,inf['parent']]);
   for name,typ,flag in inf['fields']:allfield.add(F(cls,name,typ))
   for name,args,ret,acc,code in inf['methods']:allmethod.add(M(cls,name,args,ret))
   for meth in inf['methods']:
    for op,args in meth[4].ops:
     if op=='new' or op=='array':types.add(args[-1])
     elif op=='string':strings.add(args[-1])
     elif op=='invoke':allmethod.add(args[-1])
     elif op=='iget' or op=='iput':allfield.add(args[-1])
  for f in allfield:types.update([f[0],f[2]]);strings.add(f[1])
  for m in allmethod:types.update([m[0],m[3],*m[2]]);strings.add(m[1])
  self.protos=set((m[2],m[3]) for m in allmethod)
  for typ in types:strings.add(typ)
  for args,ret in self.protos:
   shorty=lambda t:'L' if t[0] in 'L[' else t
   strings.add(shorty(ret)+''.join(shorty(a) for a in args))
  self.strings=sorted(strings,key=lambda s:s.encode('utf-16be'));self.strid={s:i for i,s in enumerate(self.strings)}
  self.types=sorted(types,key=lambda s:self.strid[s]);self.typeid={s:i for i,s in enumerate(self.types)}
  self.protos=sorted(self.protos,key=lambda p:(self.typeid[p[1]],tuple(self.typeid[a] for a in p[0])))
  self.protoid={p:i for i,p in enumerate(self.protos)}
  self.fields=sorted(allfield,key=lambda f:(self.typeid[f[0]],self.strid[f[1]],self.typeid[f[2]]));self.fieldid={m:i for i,m in enumerate(self.fields)}
  self.methods=sorted(allmethod,key=lambda m:(self.typeid[m[0]],self.strid[m[1]],self.protoid[m[2],m[3]]));self.methodid={m:i for i,m in enumerate(self.methods)}
  self.clslist=sorted(classes,key=lambda t:self.typeid[t])
 def make(self):
  strings=self.strings;types=self.types;protos=self.protos;fields=self.fields;methods=self.methods;clslist=self.clslist
  positions={};p=112
  for key,count,size in [('string_ids',len(strings),4),('type_ids',len(types),4),('proto_ids',len(protos),12),('field_ids',len(fields),8),('method_ids',len(methods),8),('class_defs',len(clslist),32)]:positions[key]=(p,count);p+=count*size
  dataoff=(p+3)&~3;data=bytearray();
  def addr():return dataoff+len(data)
  def write(b):data.extend(b)
  def a4():align(data)
  str_off=[]
  for s in strings:
   str_off.append(addr());length=len(s.encode('utf-16le'))//2;write(uleb(length)+s.encode('utf-8')+b'\0')
  a4()
  type_lists={}
  for args,ret in protos:
   if args not in type_lists and args:
    type_lists[args]=addr();write(struct.pack('<I',len(args))+b''.join(struct.pack('<H',self.typeid[t]) for t in args));a4()
  codeoffs={}
  for cls in clslist:
   for name,args,ret,acc,code in classes[cls]['methods']:
    a4();codeoffs[M(cls,name,args,ret)]=addr();words=code.words(self)
    write(struct.pack('<HHHHII',code.regs,code.ins,5,0,0,len(words)));write(struct.pack('<'+'H'*len(words),*words))
  class_data={}
  for cls in clslist:
   clsinf=classes[cls];class_data[cls]=addr();direct=[];virtual=[]
   for name,args,ret,acc,code in clsinf['methods']:
    m=M(cls,name,args,ret);(direct if name=='<init>' else virtual).append((self.methodid[m],acc,codeoffs[m]))
   inst=sorted([(self.fieldid[F(cls,n,t)],flags) for n,t,flags in clsinf['fields']]);direct.sort();virtual.sort()
   write(b''.join(uleb(x) for x in (0,len(inst),len(direct),len(virtual))))
   last=0
   for id_,flags in inst:write(uleb(id_-last)+uleb(flags));last=id_
   for methods_ in [direct,virtual]:
    last=0
    for id_,flags,c_off in methods_:write(uleb(id_-last)+uleb(flags)+uleb(c_off));last=id_
  a4();mapoff=addr()
  mapitems=[]
  for typ,key in [(1,'string_ids'),(2,'type_ids'),(3,'proto_ids'),(4,'field_ids'),(5,'method_ids'),(6,'class_defs')]:
   off,count=positions[key]
   if count:mapitems.append((typ,count,off))
  mapitems.extend([(0,1,0),(0x2002,len(strings),str_off[0])])
  if type_lists:mapitems.append((0x1001,len(type_lists),min(type_lists.values())))
  if codeoffs:mapitems.append((0x2001,len(codeoffs),min(codeoffs.values())))
  mapitems.extend([(0x2000,len(class_data),min(class_data.values())),(0x1000,1,mapoff)])
  mapitems.sort(key=lambda x:x[2]);write(struct.pack('<I',len(mapitems)))
  for typ,count,off in mapitems:write(struct.pack('<HHII',typ,0,count,off))
  end=dataoff+len(data);b=bytearray(end);b[dataoff:]=data
  for i,off in enumerate(str_off):struct.pack_into('<I',b,positions['string_ids'][0]+4*i,off)
  for i,t in enumerate(types):struct.pack_into('<I',b,positions['type_ids'][0]+4*i,self.strid[t])
  for i,(args,ret) in enumerate(protos):
   short=lambda t:'L' if t.startswith(('L','[')) else t
   sh=short(ret)+''.join(short(x) for x in args)
   struct.pack_into('<III',b,positions['proto_ids'][0]+12*i,self.strid[sh],self.typeid[ret],type_lists.get(args,0))
  for i,(cls,name,typ) in enumerate(fields):struct.pack_into('<HHI',b,positions['field_ids'][0]+8*i,self.typeid[cls],self.typeid[typ],self.strid[name])
  for i,(cls,name,args,ret) in enumerate(methods):struct.pack_into('<HHI',b,positions['method_ids'][0]+8*i,self.typeid[cls],self.protoid[args,ret],self.strid[name])
  for i,cls in enumerate(clslist):struct.pack_into('<IIIIIIII',b,positions['class_defs'][0]+32*i,self.typeid[cls],1,self.typeid[classes[cls]['parent']],0,0xffffffff,0,class_data[cls],0)
  b[0:8]=b'dex\n035\0';struct.pack_into('<I',b,32,end);struct.pack_into('<I',b,36,112);struct.pack_into('<I',b,40,0x12345678);struct.pack_into('<III',b,44,0,0,mapoff)
  struct.pack_into('<II',b,56,len(strings),positions['string_ids'][0]);struct.pack_into('<II',b,64,len(types),positions['type_ids'][0]);struct.pack_into('<II',b,72,len(protos),positions['proto_ids'][0]);struct.pack_into('<II',b,80,len(fields),positions['field_ids'][0]);struct.pack_into('<II',b,88,len(methods),positions['method_ids'][0]);struct.pack_into('<II',b,96,len(clslist),positions['class_defs'][0]);struct.pack_into('<II',b,104,end-dataoff,dataoff)
  b[12:32]=hashlib.sha1(b[32:]).digest();struct.pack_into('<I',b,8,zlib.adler32(b[12:])&0xffffffff)
  print('DEX',len(b),'strings',len(strings),'types',len(types),'methods',len(methods));return bytes(b)

def xml_manifest():
 android='http://schemas.android.com/apk/res/android'
 attrs={'label':0x01010001,'name':0x01010003,'exported':0x01010010,'minSdkVersion':0x0101020c,'versionCode':0x0101021b,'versionName':0x0101021c,'targetSdkVersion':0x01010270}
 pool=list(attrs)+['android',android,'manifest','uses-sdk','application','activity','intent-filter','action','category','package','com.apklab.workshop','0.1','APK Lab','.MainActivity','android.intent.action.MAIN','android.intent.category.LAUNCHER']
 pos={s:i for i,s in enumerate(pool)}
 def ln(n):return bytes([n]) if n<128 else bytes([0x80|(n>>8),n&255])
 chunks=bytearray();starts=[]
 for s in pool:
  starts.append(len(chunks));b=s.encode();chunks.extend(ln(len(s))+ln(len(b))+b+b'\0')
 align(chunks);size=28+len(starts)*4+len(chunks)
 sp=struct.pack('<HHIIIIII',1,28,size,len(pool),0,0x100,28+len(starts)*4,0)+b''.join(struct.pack('<I',x) for x in starts)+chunks
 rm=struct.pack('<HHI',0x180,8,8+4*len(attrs))+b''.join(struct.pack('<I',x) for x in attrs.values())
 def node(t,extra,line=1):return struct.pack('<HHIII',t,16,len(extra)+16,line,0xffffffff)+extra
 def ns(start):return node(0x100 if start else 0x101,struct.pack('<II',pos['android'],pos[android]))
 def a(name,value,typ=3):
  namespace=pos[android] if name in attrs else 0xffffffff
  raw=pos[value] if typ==3 else 0xffffffff
  d=pos[value] if typ==3 else value
  return struct.pack('<IIIHBBI',namespace,pos[name],raw,8,0,typ,d)
 def start(name,attrslist=[]):
  extra=struct.pack('<IIHHHHHH',0xffffffff,pos[name],20,20,len(attrslist),0,0,0)+b''.join(a(*item) for item in attrslist)
  return node(0x102,extra)
 def stop(name):return node(0x103,struct.pack('<II',0xffffffff,pos[name]))
 chunks=[sp,rm,ns(True),start('manifest',[('package','com.apklab.workshop',3),('versionCode',1,16),('versionName','0.1',3)]),start('uses-sdk',[('minSdkVersion',24,16),('targetSdkVersion',28,16)]),stop('uses-sdk'),start('application',[('label','APK Lab',3)]),start('activity',[('name','.MainActivity',3),('exported',1,18)]),start('intent-filter'),start('action',[('name','android.intent.action.MAIN',3)]),stop('action'),start('category',[('name','android.intent.category.LAUNCHER',3)]),stop('category'),stop('intent-filter'),stop('activity'),stop('application'),stop('manifest'),ns(False)]
 body=b''.join(chunks);return struct.pack('<HHI',3,8,8+len(body))+body

def main():
 (ROOT/'build').mkdir(parents=True,exist_ok=True)
 dex=Dex().make();xml=xml_manifest();(ROOT/'build'/'classes.dex').write_bytes(dex);(ROOT/'build'/'AndroidManifest.xml').write_bytes(xml)
 with zipfile.ZipFile(OUT,'w') as z:
  z.writestr('AndroidManifest.xml',xml,compress_type=zipfile.ZIP_STORED)
  z.writestr('classes.dex',dex,compress_type=zipfile.ZIP_DEFLATED)
  z.write(ROOT/'assets'/'index.html','assets/index.html',compress_type=zipfile.ZIP_DEFLATED)
 # Release signing MUST use a long-lived key stored outside git (for example Actions secrets).
 # Without release secrets this produces a disposable, development-only APK.
 key_b64=os.getenv('APKLAB_RELEASE_KEYSTORE_B64')
 ks=ROOT/'build'/'keystore.jks'
 if key_b64:
  ks.write_bytes(base64.b64decode(key_b64,validate=True))
  store=os.environ['APKLAB_STORE_PASSWORD']
  keypass=os.getenv('APKLAB_KEY_PASSWORD') or store
  alias=os.environ['APKLAB_KEY_ALIAS']
  print('Signing with external release keystore')
 else:
  store=secrets.token_urlsafe(22)
  keypass=store
  alias='apklab-dev'
  ks.unlink(missing_ok=True)  # never reuse a development key
  print('WARNING: development APK with an ephemeral key; NOT for store releases')
  subprocess.run(['keytool','-genkeypair','-alias',alias,'-keyalg','RSA','-keysize','2048','-validity','3650','-dname','CN=APK Lab Development,O=APK Lab,C=US','-storepass',store,'-keypass',keypass,'-keystore',str(ks),'-storetype','PKCS12','-noprompt'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 subprocess.run(['jarsigner','-keystore',str(ks),'-storepass',store,'-keypass',keypass,'-digestalg','SHA-256','-sigalg','SHA256withRSA',str(OUT),alias],check=True,stdout=subprocess.PIPE)
 if not key_b64:
  ks.unlink(missing_ok=True)
 print('APK',OUT,OUT.stat().st_size)
if __name__=='__main__':main()