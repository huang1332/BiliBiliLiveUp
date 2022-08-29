import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import pickle,traceback,time
import subprocess,os
import sys,random,shutil

exec_path=r'/root/b'
#dotnet cil/BililiveRecorder.Cli.dll  run --bind "http://*:11419" "/root/b/work"

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        #可以选择"w"
        self.log = open(filename, "a", encoding="utf-8")  # 防止编码错误
    def write(self, message):
        self.terminal.write(message)
        self.log.write(time.strftime("\n%Y-%m-%d %H:%M:%S\n", time.localtime())+message)
    def flush(self):
        pass
    def reset(self):
        self.log.close()
        sys.stdout=self.terminal
def rename(streamer,mid_title,vid_path):
    full_title=mid_title+'[直播回放]'
    streamer_head='['+streamer+']'
    time_head='['+vid_path[vid_path.find('/')+1:vid_path.find('-')]+'录播]'
    limit=79-len(streamer_head+time_head)
    return streamer_head+time_head+full_title[:limit]
def change_yaml(RoomId,streamer,mid_title,full_title_now,vid_path):
    yaml0=open('yaml/'+'model.yaml','r',encoding='utf-8')
    yaml1=yaml0.readlines()
    yaml0.close()
    yaml1[3]='  '+'work/'+vid_path+':\n'
    yaml1[5]='    source: "https://live.bilibili.com/'+RoomId+'"\n'
    if os.path.exists('work/'+vid_path.replace('.flv','.cover.jpg')):
        yaml1[7]='    cover: "'+'work/'+vid_path.replace('.flv','.cover.jpg')+'"\n'
    else:
        print('cover not found '+vid_path.replace('.flv','.cover.jpg'))
    yaml1[8]='    title: "'+full_title_now+'"\n'
    yaml1[10]='    desc: "请务必关注一下这么可爱的'+streamer+'！直播间原标题: '+mid_title+'"\n'
    yaml1[12]='    dynamic: "#'+streamer+'#"\n'
    yaml1[16]='    tag: "VTuber,'+streamer+',vtuber,VUP,直播录像,可爱,生肉,VTB,虚拟主播,虚拟YOUTUBER"\n'
    with open('yaml/'+RoomId+'.yaml','w',encoding='utf-8') as h:
        h.writelines(yaml1)
def biliup(RoomId,exec_path):
    proc = subprocess.Popen(exec_path+"/biliup upload --config "+exec_path+"/yaml/"+RoomId+".yaml",
                            shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                            cwd =exec_path)
    print('subprocess '+exec_path+"/biliup upload --config "+exec_path+"/yaml/"+RoomId+".yaml")
    outs, errs=b'',b''
    try:
        outs, errs = proc.communicate(timeout=1200)
        proc.kill()
    except subprocess.TimeoutExpired:
        print('subprocess.TimeoutExpired')
        proc.kill()
    outs=outs.decode("utf-8","ignore")
    errs=errs.decode("utf-8","ignore")
    print(outs,errs)
    if '成功' in outs and '"aid":' in outs and '"bvid":' in outs:
        aid=outs[outs.find('"aid":')+6:outs.find(',"bvid":')]
        if aid.isdigit():
            print('aid解析成功 '+aid)
            return aid
        else:
            print('aid解析不成功 '+aid)
    else:
        print('out解析不成功','成功' in outs ,'"aid":' in outs ,'"bvid":' in outs)
    return 'empty'
def biliup_apd(vid_path,vid_last,exec_path):
    proc = subprocess.Popen(exec_path+"/biliup append --vid "+vid_last+" "+exec_path+"/"+'work/'+vid_path+' --limit 2 --line kodo',
                            shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd =exec_path)
    print('subprocess '+exec_path+"/biliup append --vid "+vid_last+" "+exec_path+"/"+'work/'+vid_path+' --limit 2 --line kodo')
    outs, errs=b'',b''
    try:
        outs, errs = proc.communicate(timeout=1200)
        proc.kill()
    except subprocess.TimeoutExpired:
        print('subprocess.TimeoutExpired')
        proc.kill()
    outs=outs.decode("utf-8","ignore")
    errs=errs.decode("utf-8","ignore")
    print(outs,errs)
    if '成功' in outs and '"aid":' in outs and '"bvid":' in outs:
        aid=outs[outs.find('"aid":')+6:outs.find(',"bvid":')]
        if aid.isdigit():
            print('aid解析成功 '+aid)
            return aid
        else:
            print('aid解析不成功 '+aid)
    else:
        print('out解析不成功','成功' in outs ,'"aid":' in outs ,'"bvid":' in outs)
    return 'empty'
def last_w(RoomId,mid_title,vid):
    g=open('pkl/'+RoomId+'.pkl','wb')
    pickle.dump((mid_title,vid),g)
    g.close()
def last_r(RoomId,mid_title):
    if os.path.exists('pkl/'+RoomId+'.pkl'):
        with open('pkl/'+RoomId+'.pkl','rb') as g:
            mid_title_last,vid_last= pickle.load(g)
            if mid_title==mid_title_last and vid_last.isdigit():
                return vid_last
    else:
        print('pkl exists error '+'pkl/'+RoomId+'.pkl')
    return 'empty'
def last_remove(RoomId):
    if os.path.exists('pkl/'+RoomId+'.pkl'):
        os.remove('pkl/'+RoomId+'.pkl')


def sub_once(str_exec,sub_timeout=999):
    #print(str_exec)
    proc = subprocess.Popen(str_exec, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        outs, errs = proc.communicate(timeout=sub_timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        print('timeout',str_exec)
        outs, errs=b'',b''
    if errs!=b'':
        pass#print(errs.decode())
    return outs.decode(), errs.decode()

def copy_(local_path,remote_path,file_name=''):
    local_file,remote_file=local_path+'/'+file_name,remote_path+'/'+file_name
    if file_name=='':
        sub_call=[exec_path+'/rclone/'+'rclone','copy',local_path,remote_path]
    else:
        sub_call=[exec_path+'/rclone/'+'rclone','copy',local_file,remote_path]
    outs, errs=sub_once(sub_call)
    #print(outs, errs)
    if errs=='' :#and path_exist(remote_path) 
        print('rclone_ok'+' '+local_path+' '+remote_path+' '+file_name)
        return True
    else :
        print('rclone_error4'+' '+local_path+' '+remote_path+' '+file_name+' '+errs)
        return False



def run(RoomId,msg):
    streamer,mid_title,vid_path=msg['Name'],msg['Title'],msg['RelativePath']
    
    sys.stdout = Logger(streamer+'.txt')
    print(msg)
    full_title_now=rename(streamer,mid_title,vid_path)
    vid_last=last_r(RoomId,mid_title)
    if vid_last!='empty':
        vid_now=biliup_apd(vid_path,vid_last,exec_path)
        if vid_last!=vid_now:
            print('vid_last!=vid_now '+vid_last+' '+vid_now)
    else:
        change_yaml(RoomId,streamer,mid_title,full_title_now,vid_path)
        vid_now=biliup(RoomId,exec_path)
        
    if vid_now!='empty':
        last_w(RoomId,mid_title,vid_now)
    else:
        for i in range(3):
            time.sleep(i*60)
            print('vid_now==empty error '+streamer)
            change_yaml(RoomId,streamer,mid_title,full_title_now,vid_path)
            vid_now=biliup(RoomId,exec_path)
            if vid_now!='empty':
                last_w(RoomId,mid_title,vid_now)
                break
    roomid,vid_name=vid_path.split('/')
    if roomid!=RoomId:
        print('roomid!=RoomId '+roomid+' '+RoomId)
    cover_path=exec_path+'/work/'+vid_path.replace('.flv','.cover.jpg')
    for i in range(2):
        time.sleep(i*60)
        remote_='one:bil/'+roomid+'/'+time.strftime("%Y-%m",time.localtime())
        if copy_(exec_path+'/work/'+roomid,remote_,file_name=vid_name):
            os.remove(exec_path+'/work/'+vid_path)
            if os.path.exists(cover_path):
                os.remove(cover_path)
            print('rm vid ok '+vid_path+' '+'one:bil/'+roomid)
            break
    if os.path.exists(exec_path+'/work/'+vid_path):
        os.remove(exec_path+'/work/'+vid_path)
    if os.path.exists(cover_path):
        os.remove(cover_path)
    sys.stdout.reset()

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            self.send_response(200)
            self.end_headers()
            data = self.rfile.read(int(self.headers['content-length']))
            json_msg = json.loads(data)
            print(json_msg)
            if 'EventType' in json_msg:
                if json_msg['EventType']=='FileClosed':
                    msg=json_msg['EventData']
                    RoomId=str(msg['RoomId'])
                    t=threading.Thread(target=run, args=(RoomId,msg))
                    t.start()
                elif json_msg['EventType']=='StreamEnded':
                    msg=json_msg['EventData']
                    last_remove(str(msg['RoomId']))
        except:
            print(traceback.format_exc())           

        
if __name__ == "__main__":
    if not os.path.exists('drive'):
        os.mkdir('drive')
    if not os.path.exists('pkl'):
        os.mkdir('pkl')
    if not os.path.exists('work'):
        os.mkdir('work')
    addr = ('127.0.0.1', 1315)
    server = HTTPServer(addr, RequestHandler)
    server.serve_forever()
