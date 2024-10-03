#jupyter lab --ip=0.0.0.0 --config jupyter_config.py --port=8887

from jupyter_server.auth.identity import PasswordIdentityProvider

c.ServerApp.allow_remote_access = True
c.ServerApp.allow_origin = '*'
c.ServerApp.root_dir = "/home/user"

PasswordIdentityProvider.hashed_password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$Ct7uQIdNDrPp6LHrGPfANQ$jq/RQiaN7fLxa4biy3G87Dz26DRRzM0ZEf0xqGuKkdI'
