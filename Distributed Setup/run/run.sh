if [[ $(docker ps -q $1 | wc -l) -gt 0 ]] ; then docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q); fi  
docker run -d --env-file /tmp/mxnet_env/worker --name worker_2 -v /mnt/mxnet-test/incubator-mxnet:/incubator-mxnet -w /incubator-mxnet/example/image-classification/ --net=host abhin99/mxnet python3 train_cifar10.py --network resnet --num-layers 110 --batch-size 64 --num-epochs 5 --disp-batches 1 --loss ce --kv-store dist_sync
docker logs -f worker_2 &> resnet-110_64-cifar10_logs_worker_2_2_2.log &
