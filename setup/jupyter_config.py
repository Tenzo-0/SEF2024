#jupyter lab --ip=0.0.0.0 --config config.py --port=8887

from jupyter_server.auth.identity import PasswordIdentityProvider

c.ServerApp.allow_remote_access = True
c.ServerApp.allow_origin = '*'
c.ServerApp.root_dir = "/home/user/notebooks"

PasswordIdentityProvider.hashed_password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$Z3Fb2goTsoEu7JoaNqxzfA$QI+UWp2+4Mae8xW85EZ2p2+cI4emAGbOZroQy/SmyKE'
