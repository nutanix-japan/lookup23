# Cloudflare Tunnel
## Setup CloudFlare Tunnel
1. Go to Zerotrust > Networks > + Create a Tunnel
2. Select Cloudflared
3. Click on Next 
4. Give a name to your tunnel
5. Click on Save Tunnel
6. Copy the Tunnel Token from the commmands for your host environment

## Create your App and Tunnel Containers

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
4. Make sure the containers are running and check status in CloudFlare > Zerotrust > Networks > Tunnels > ``your-tunnel``

## Create CNAME and Map to Container

1. Go CloudFlare > Zerotrust > Networks > Tunnels > ``your-tunnel``
2. Go to Public Hostname
3. Click on ``Add a public hostname``
4. Create a subdomain ``lookup-country``
5. Choose the base domain
6. Choose HTTP as the Service
7. Input the host IP addres as the URL with the host port number where the container is exposed
    
    ```url
    10.x.x.19:8080
    ```

## Create OTP App

1. In Zero Trust ↗, go to Access > Applications.
2. Click on Add Applications
3. Provide a name
4. Select a sesssion duration   
5. For application domain
   
   - Subdomain - use the subdomain created before
   - Domain - select the base domain 
   - Path - optional 

6. Identity provides - One-time PIP
7. Choose the email domains that you would like allow

Browse to you ``subdomain.domain.com`` with a secure SSL cert. 

That's it

