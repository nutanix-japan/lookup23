# Created to lookup cluster details

Aim is not re-invent the wheel. But couldn't find any older code.

At least learned some front-end stuff along the way. 

Clone repo

```bash
git clone https://github.com/nutanix-japan/lookup23/
```

Docker build

```bash
docker build -t lookup23 .
```
# Docker Compose

1. Install ``docker-compose``
2. Fill in the following ``docker-compose.yaml`` file
   
    ```yaml
    version: '3.3'

    # networks:
    #   lookup23_default:
    #     external: true

    services: 
    # # Lookup container starts here 
      lookup:
        image: lookup23
        container_name: lookup23
        restart: unless-stopped
        security_opt:
        - no-new-privileges:true
        ports:
        - 8080:8000

      tunnel:
        image: cloudflare/cloudflared
        restart: unless-stopped
        command: tunnel run
        # networks:
        #   - lookup23_default
        environment:
            - TUNNEL_TOKEN=xxxxxxxx
    ```
3. Run the containers
    
    ```bash
    docker compose up -d
    ```
