# Setup the ssh server configuration and keys

set -e

# create an ssh key for the root user
mkdir -p /root/.ssh
ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ""

# allow the key to be used to authenticate ssh connections
cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys

# configure the ssh server to allow the root user to login only with an ssh key
echo "PermitRootLogin without-password" >> /etc/ssh/sshd_config

# generate a unique host key
ssh-keygen -A
