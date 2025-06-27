# eramba-worker-autoscaler
Auto-scaling of workers for Eramba 3.25.2

# How to run it :

```bash

docker compose -f your-current-compose.yml -f docker-compose.yml -f docker-compose.simple-install.enterprise.yml up -d  --build

# your-current-compose.yml : Your current compose file that run stack 
# docker-compose.yml : copy this from the current repository 
# docker-compose.simple-install.enterprise.yml : For those who are using ERAMBA enterprise. 

```
# To follow the event of autoscaler run!
```bash

docker compose -f your-current-compose.yml -f docker-compose.yml -f docker-compose.simple-install.enterprise.yml logs -f --tail=10 log-watcher

# your-current-compose.yml : Your current compose file that run stack 
# docker-compose.yml : copy this from the current repository 
# docker-compose.simple-install.enterprise.yml : For those who are using ERAMBA enterprise. 

```



