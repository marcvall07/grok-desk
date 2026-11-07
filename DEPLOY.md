# Deploy notes for Railway / Render

1. Create a GitHub repo and push the desk/ folder
   (do NOT commit TG_TOKEN or any secrets)

2. Railway:
   - New Project → Deploy from GitHub
   - Add variables:
     TG_TOKEN = 8820... (your bot token)
     DATA_PATH = mxyBeeDto79uuE75jmEgAl74p8XYZbPK89u4FgO_nsc
   - Start command is already in Procfile

3. After deploy you get a URL like https://xxx.up.railway.app
   Open on phone:
   https://xxx.up.railway.app/#d=mxyBeeDto79uuE75jmEgAl74p8XYZbPK89u4FgO_nsc

4. The process stays running, Telegram + PumpPortal stay connected,
   and the app polls live JSON.
