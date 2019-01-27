# Server Configuration
In this project I configured a linux server to serve the item catalog application.
I've learnt these skills:
- user management (giving sudo permission, authentication with key pairs)
- Firewall configuration
- Postgresql installation and creation of roles
- Apache configuration
- Python WSGI

---

## Server Connect Info For Grader
- IP: 54.
- SSH port: 2200
- passphrase: fsnd

---

## The complete URL to your hosted web application.
Locate the SSH key you created for the grader user.

During the submission process, paste the contents of the grader user's SSH key into the "Notes to Reviewer" field.

---

## User creation
1. First, I created the `grader` user with password `fsnd` (`sudo adduser grader`)
2. I made `grader` a sudoer by adding `/etc/sudoers.d/grader`
3. In my local/real computer I generated a **key pair** with `ssh-keygen` named `server_config` with passphrase `fsnd`
4. I enabled password login: `sudo nano /etc/ssh/sshd_config`, `PasswordAuthentication no`
   so `grader` could log in
5. Then, I installed the public key in server:
    1. Log in with grader
    2. `mkdir /home/grader/.ssh`
    3. `touch .ssh/authorized_keys`
    4. Paste the `server_config.pub` contents in `.ssh/authorized_keys`
    5. `chmod 700 .ssh` (TODO)
    6. `chmod 644 .ssh/authorized_keys` (TODO)
6. `ssh grader@52.91.4.83 -p 22`
7. I disabled password login
8. Finally, I restarted ssh with `sudo service ssh restart`

---

## Update packages
```
sudo apt-get update
sudo apt-get upgrade
```
The first one updates the packages list; the second updates the programs.

---

## Firewall
I denied all incoming connections, allowing only SSH (for me to connect) and HTTP (for serving the web app).

```
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow www

sudo ufw enable
```

#### SSH port:
1. In Lightsail, in the networking section, open the 2200/tcp port
2. Add 2200 as an ssh port in `/etc/ssh/sshd_config`
3. `sudo ufw allow 2200/tcp`
4. Reboot virtual machine
5. Log in again through port 2200 and deny port 22 access (with ufw and in ssh config)

---

## Timezone UTC
`sudo dpkg-reconfigure tzdata`

---

## Postgresql setup
1. Install postgresql:
   ```
   sudo apt-get install postgresql postgresql-contrib
   ```
2. Change postgre authentication to allow password login (the default one needs to have a linux user same as the role name). I followed the instructions from:
- https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04
- https://stackoverflow.com/questions/18664074/getting-error-peer-authentication-failed-for-user-postgres-when-trying-to-ge
3. Then I created the `catalog` role with `dbpw` password.

---

## Project
1. Install git: `sudo apt-get git`
2. Download code with `grader` user at `/home/grader/fsnd_projects`: `git clone https://github.com/ziggylineous/udacity-full-stack-dev.git fsnd_projects`

Another way to have the project would have been to use `scp`, to copy from my machine to the server

---

## Apache 
#### Resources for this section:
- https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
- http://leonwang.me/post/deploy-flask
- http://flask.pocoo.org/docs/1.0/deploying/mod_wsgi/

#### Installation
Install Apache Http Server (apache2 package).
In order for apache to pass the requests to the python app, we need install **wsgi**

```
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi-py3
```

#### Apache and WSGI configurations
Configure the site at `/etc/apache2/sites-enabled/item_catalog.conf`.
Enable mod_wsgi: `sudo a2enmod wsgi`
Anytime something changed run: `sudo service apache2 restart`

#### WSGI script
1. Activates the python app's enviroment (without this, the modules aren't found)
2. Import the app as `application`
3. Log setup

#### Resources paths (client_secret.json and index)
Apache manages at its will the current directory, so you cannot trust that the current directory is always the same. Because of this, the relative paths fail (if the server decides to change the current directory). This was taken from https://modwsgi.readthedocs.io/en/develop/user-guides/application-issues.html#application-working-directory. 


So I had to change the relative paths for the item search index and for the google's client_secret.json:
```
import os
from os.path import abspath, dirname

index_path = os.path.join(
    abspath(dirname(__file__)),
    '..',
    'index'
)

google_auth_json = os.path.join(
    abspath(dirname(__file__)),
    '..',
    'client_secret.json'
)
```