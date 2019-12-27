# Fire-TV - plugin pour Domoticz

* Ce  plugin n'est pas maintenu


fire-tv permet de contrôler une clé amazon «fire tv» depuis domoticz.

Je l'utilise sur un raspberry pi 3, OS raspbian buster.

Ce plugin utilise le protocole CEC pour dialoguer avec la clé, le téléviseur et la barre de son, ainsi que adb pour obtenir certaines informations de la clé.

- Note 1 : le protocole CEC est souvent très mal implémenté par les fabricants, dans ce cas certaines fonctions ne seront pas opérationnelles. Par exemple sur les téléviseurs LG il n'est pas possible de mettre en veille ni de contrôler le son...
- Note 2 : certains appareils qui n'implémentent pas le protocole CEC rendent carrément le bus CEC inopérant.
- Note 3 : la langue par défaut du plugin est l'espéranto. Seule la traduction en français est disponible.

## pré-requis :
- Le serveur domoticz relié en HDMI au téléviseur avec un câble compatible CEC.
- Une adresse IP fixe pour le «fire TV».
- Une carte graphique compatible CEC. La carte graphique intégrée au raspberry Pi 3 l'est.
- adb activé sur le «fire TV».
- adb installé et opérationnel sur le serveur.
- libcec4 installé sur le serveur.

## exemple d'installation d'adb :
### sur la clé «fire TV» :
aller dans le menu paramètres, puis «Ma Fire TV», puis «Options pour les développeurs», puis mettre «Débogage ADB» sur OUI.
### sur le raspberry, avec un fire TV dont l'adresse IP est 192.168.1.10 :
```bash
sudo aptitude install adb
adb connect 192.168.1.10:5555
```
### à ce moment là, un message apparait sur le téléviseur demandant si on autorise le débogage.
Cocher «Toujour autoriser...», puis faire OK.
### sur le raspberry : 
```bash
adb disconnect
adb kill-server
```


## exemple d'installation de libcec4 :
### sur le raspberry :
```bash
sudo apt-get update
sudo apt-get install cmake libudev-dev libxrandr-dev python-dev swig
mkdir ~/src
cd ~/src
git clone https://github.com/Pulse-Eight/platform.git
mkdir platform/build
cd platform/build
cmake ..
make
sudo make install
cd ~/src
git clone https://github.com/Pulse-Eight/libcec.git
mkdir libcec/build
cd libcec/build
cmake -DRPI_INCLUDE_DIR=/opt/vc/include -DRPI_LIB_DIR=/opt/vc/lib ..
make -j4
sudo make install
sudo ldconfig
echo "scan" | cec-client -s -d 1
```

## exemple d'installation du plugin :
### sur le raspberry :
```bash
cd ~/domoticz/plugins
git clone https://github.com/jmichault/fire-tv
```
### dans domoticz :
aller dans Réglages, Matériel.\
dans type, sélectionner «Amazon Fire TV (with Kodi remote)»\
renseigner le nom.\
renseigner l'adresse IP.\
si vous n'avez pas de barre de son ou de home cinéma, mettre 0 dans le «CEC ID for sound». (Note : pas testé).\
cliquer «Ajouter».

Vous devriez maintenant avoir deux nouveaux périphériques dans l'onglet «Interrupteurs» :
- le premier (statut) permet d'une part d'allumer/éteindre fireTV, télé et barre de son, d'autre part de simuler la télécommande.
- le deuxième (Application) permet de lancer d'un seul clic mes applications préférées : netflix, molotov, kodi et spotify.

