from fabric import Connection
from fabric import SerialGroup


def schedulerEnv(rootUri,n_ps,n_w):
    file=open("scheduler","w")
    L = ["DMLC_ROLE=scheduler\n","DMLC_PS_ROOT_URI="+str(rootUri)+"\n","DMLC_PS_ROOT_PORT=9091\n","DMLC_NUM_SERVER="+str(n_ps)+"\n","DMLC_NUM_WORKER="+str(n_w)+"\n"]
    file.writelines(L)
    file.close()
    Connection(rootUri).run('sudo mkdir -p /tmp/mxnet_env && sudo chmod 777 /tmp/mxnet_env')
    Connection(rootUri).put('scheduler', '/tmp/mxnet_env')
    print(rootUri+" scheduler env set")

def serverEnv(rootUri,nodeHost,n_ps,n_w):
    file=open("server","w")
    L = ["DMLC_ROLE=server\n","DMLC_PS_ROOT_URI="+str(rootUri)+"\n","DMLC_PS_ROOT_PORT=9091\n","DMLC_NODE_HOST="+str(nodeHost)+"\n","DMLC_SERVER_ID=0\n""DMLC_NUM_SERVER="+str(n_ps)+"\n","DMLC_NUM_WORKER="+str(n_w)+"\n"]
    file.writelines(L)
    file.close()
    Connection(nodeHost).run('sudo mkdir -p /tmp/mxnet_env && sudo chmod 777 /tmp/mxnet_env')
    Connection(nodeHost).put('server', '/tmp/mxnet_env')
    print(nodeHost+" server env set")
    

def WorkerEnv(rootUri,nodeHost,n_ps,n_w):
    file=open("worker","w")
    L = ["DMLC_ROLE=worker\n","DMLC_PS_ROOT_URI="+str(rootUri)+"\n","DMLC_PS_ROOT_PORT=9091\n","DMLC_NODE_HOST="+str(nodeHost)+"\n","DMLC_SERVER_ID=0\n""DMLC_NUM_SERVER="+str(n_ps)+"\n","DMLC_NUM_WORKER="+str(n_w)+"\n"]
    file.writelines(L)
    file.close()
    Connection(nodeHost).run('sudo mkdir -p /tmp/mxnet_env && sudo chmod 777 /tmp/mxnet_env')
    Connection(nodeHost).put('worker', '/tmp/mxnet_env')
    print(nodeHost+" worker env set")

def startScript(name,idx,nodeHost,ps,worker,job):
    file=open("run.sh","w")
    tempName = name
    name = str(name)+"_"+str(idx)
    name = str(name)
    # print(name)
    ps = str(ps)
    worker = str(worker)
    L = list()
    check = "if [[ $(docker ps -q $1 | wc -l) -gt 0 ]] ; then docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q); fi  \n"
    L.append(check)
    w = "docker run -d --env-file /tmp/mxnet_env/worker --name " + name + " -v /mnt/mxnet-test/incubator-mxnet:/incubator-mxnet -w /incubator-mxnet/example/image-classification/ --net=host abhin99/mxnet python3 train_cifar10.py --network resnet --num-layers 110 --batch-size 64 --num-epochs 5 --disp-batches 1 --loss ce --kv-store dist_sync\n"
    sch = "docker run -d --env-file /tmp/mxnet_env/scheduler --name " + name + " -v /mnt/mxnet-test/incubator-mxnet:/incubator-mxnet -w /incubator-mxnet/example/image-classification/ --net=host abhin99/mxnet python3 train_cifar10.py --network resnet --num-layers 110 --batch-size 64  --num-epochs 5 --disp-batches 1 --loss ce --kv-store dist_sync\n"
    if(tempName=='scheduler'):
        name='server'
        name = str(name)+"_"+str(idx)
    s = "docker run -d --env-file /tmp/mxnet_env/server --name " + name + " -v /mnt/mxnet-test/incubator-mxnet:/incubator-mxnet -w /incubator-mxnet/example/image-classification/ --net=host abhin99/mxnet python3 train_cifar10.py --network resnet --num-layers 110 --batch-size 64 --num-epochs 5  --disp-batches 1 --loss ce --kv-store dist_sync\n"
    workerLogs = 'docker logs -f '+name+' &> '+job+'_'+'logs_'+name+'_'+ps+'_'+worker+'.log &\n'
    if tempName=='worker' :
        print("in worker")
        L.append(w)
        L.append(workerLogs)
    elif tempName=='server':
        print("in server")
        L.append(s)
    elif tempName=='scheduler':
        print("in scheduler")
        L.append(sch)
        L.append(s)
    # metrics = 'while [ $(docker ps -q $1 | wc -l) -gt 0 ];do docker stats --no-stream | tee --append stats_'+name+'_'+ps+'_'+worker+'.csv;sleep 1;done &'
    # L.append(metrics
    # print(L)
    file.writelines(L)
    file.close()
    Connection(nodeHost).run('sudo mkdir -p /benchmarks && sudo chmod 777 /benchmarks')
    Connection(nodeHost).put('run.sh', '/benchmarks')
    Connection(nodeHost).run('sudo chmod 777 /benchmarks/run.sh')
    print(nodeHost+" "+name+" start script set")



# assume 1 VM = 1 Container

MasterIP = '10.142.0.2'
hosts = [MasterIP,'10.142.0.3','10.142.0.4','10.142.0.6']
rootUri = hosts[0]
hostsDict = dict()
ps = 2
worker = 2
job = "resnet-110_64-cifar10"

# sanity check

if((ps + worker)>len(hosts)):
    print("Error resouces not sufficient")

else:

    toallocServer = 1 # track allocated resources

    for i in range(ps):
        if(i==0):
            schedulerEnv(rootUri,ps,worker)
            # print("scheduler",hosts[i])
            hostsDict[hosts[i]] = "server_"+str(toallocServer)
            serverEnv(rootUri,hosts[i],ps,worker)
            # print("server",hosts[i])
            startScript('scheduler',toallocServer,hosts[i],ps,worker,job)
        else:
            # print("server",hosts[i])
            hostsDict[hosts[i]] = "server_"+str(toallocServer)
            serverEnv(rootUri,hosts[i],ps,worker)
            startScript('server',toallocServer,hosts[i],ps,worker,job)
        toallocServer = toallocServer + 1

        # serverEnv(rootUri,hosts[i],ps,worker)
    
    toallocWorker = 1
    for i in range(ps,ps+worker):
        # print("worker",hosts[i])
        hostsDict[hosts[i]] = "worker_"+str(toallocWorker)
        WorkerEnv(rootUri,hosts[i],ps,worker)
        startScript('worker',toallocWorker,hosts[i],ps,worker,job)
        toallocWorker = toallocWorker + 1


req = list()
for i in range(ps+worker):
    # print(hosts[i])
    req.append(hosts[i])
    # Connection(hosts[i]).run("cd /benchmarks && sudo bash run.sh")
    # print("running script on ",hosts[i])


SerialGroup(*req).run("cd /benchmarks && sudo bash run.sh")

for i in range(ps+worker):
    Connection(hosts[i]).run('cd /benchmarks && sudo rm -f metrics.csv && bash -c "( (nohup ./metrics.sh >'+job+'_'+'metrics_'+hostsDict[hosts[i]]+'_'+str(ps)+'_'+str(worker)+'.csv 2>&1 &) )"')
    print("metrics",hosts[i])

# result = Connection('10.142.0.2').run('uname -s',hide = True)
# msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
# print(msg.format(result))
