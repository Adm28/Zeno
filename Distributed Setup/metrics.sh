while [ $(docker ps -q $1 | wc -l) -gt 0 ];do docker stats --no-stream | tee --append metrics.csv;sleep 1;done 
