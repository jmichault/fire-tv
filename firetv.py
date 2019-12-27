#
# Amazon Fire-tv
#

try:
    import Domoticz
except ImportError:
    import fakeDomoticz as Domoticz

from adb_shell.adb_device import AdbDevice
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

import logging

import cec

def LogCallback(level, time, message):
    if level == cec.CEC_LOG_ERROR:
        levelstr = _("ERARO:   ")
    elif level == cec.CEC_LOG_WARNING:
        levelstr = _("AVERTO: ")
    elif level == cec.CEC_LOG_NOTICE:
        levelstr = _("RIMARKO:  ")
    elif level == cec.CEC_LOG_TRAFFIC:
        levelstr = _("TRAFIKO: ")
    elif level == cec.CEC_LOG_DEBUG:
        levelstr = _("ELPURIGO:   ")
    Domoticz.Debug(levelstr + "[" + str(time) + "]     " + message)
    return 0


class FiretvRC:

# inicializo : legi parametrojn, konekti kun CEC
    def __init__(self, host, cecid_sound, cecid_fire):  
        Domoticz.Debug("[FireTVRC init] cecid_sound: "+str(cecid_sound)+", cecid_fire:"+str(cecid_fire) );
        self._host = host
        self._cecid_sound = cecid_sound
        self._cecid_fire = cecid_fire
        self._device = None
        self._device = AdbDevice(serial=host+':5555');
        self._device.close();
        cecconfig = cec.libcec_configuration()
        cecconfig.strDeviceName = "libCEC"
        cecconfig.bActivateSource = 0
        cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
        cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
        #cecconfig.SetLogCallback(LogCallback)
        self.cecadapt = cec.ICECAdapter.Create(cecconfig)
        self.adapter = self.cecadapt.DetectAdapters()[0].strComName
        self.cecadapt.Open(self.adapter)
        Domoticz.Debug(_("[inicializo]  " ));

# konekti kun ADB
    def konekti(self):
        with open('/home/pi/.android/adbkey') as f:
            priv = f.read();
        try:
            self._device.close();
        except:
            Domoticz.Debug(_("[konekti] Rezulto: escepto" ));
        self._signer = PythonRSASigner('', priv);
        self._device.connect(rsa_keys=[self._signer]);

# malkonekti de ADB
    def malkonekti(self):
        self._device.close();
# sendi klavo kun ADB
    def sendiKlavo(self,klavo):
        self.konekti();
        self._device.shell("input keyevent "+ klavo);
        #self.malkonekti();

# sendi klavo kun CEC
    def sendiCecKlavo(self,dest,klavo):
        Domoticz.Debug("[sendi cec klavo] dest: "+str(dest)+", klavo:"+str(klavo) );
        ret = self.cecadapt.SendKeypress(dest,klavo)
        if not ret:
            self.cecadapt.Open(self.adapter)
            ret = self.cecadapt.SendKeypress(dest,klavo)
# akiri potencŝtato
    def akiri_potencsxtato(self):
        """Akiri potencon: malŝaltita, aktiva, atendata."""
        return_value = 'off' # implicite la «fire-TV» estas supozita malŝaltita
        ## fireTV, same kiel LG-televidiloj, ne respondas, ni ricevas ĉiam «aktiva» !!!, do CEC ne uzeblas
        #ret = self.cecadapt.GetDevicePowerStatus(self._cecid_fire)
        #Domoticz.Debug("[akiri potencŝtato] Rezulto: "+str(ret) );
        #if ret == 0:
        #    return_value = "active"
        #else:
        #    return_value = "off"
        try:
            Domoticz.Debug(_("[akiri potencŝtato] " ));
            return_value = self._device.shell("dumpsys power | grep 'Display Power' | grep -q 'state=ON' && echo -e 'active\c' || echo -e 'off\c' ");
            Domoticz.Debug(_("[akiri potencŝtato] Rezulto: " ));
        except:
            self.konekti();
            Domoticz.Debug(_("[akiri potencŝtato] Rezulto: escepto" ));
        #self.malkonekti();
        return return_value

    def apo(self,programaro):
        self.konekti();
        command = "monkey -p "+programaro+" 1";
        Domoticz.Debug(_("[apo]: ")+command );
        line = self._device.shell(command);
        #self.malkonekti();

    def klavo_sxalti(self):
        ret = self.cecadapt.PowerOnDevices(self._cecid_sound)
        if not ret:
            self.cecadapt.Open(self.adapter)
            ret = self.cecadapt.PowerOnDevices(self._cecid_sound)
        ret = self.cecadapt.PowerOnDevices(self._cecid_fire)
        ret = self.cecadapt.PowerOnDevices()
	
        #self.sendiCecKlavo(0x10,0x6d);
        #self.sendiCecKlavo(self._cecid_sound,0x6d);
        #self.sendiCecKlavo(self._cecid_fire,0x6d);
        #self.sendiKlavo("224");
        
    def klavo_malsxalti(self):
        ret = self.cecadapt.StandbyDevices()
        if not ret:
            self.cecadapt.Open(self.adapter)
            ret = self.cecadapt.StandbyDevices()
        ret = self.cecadapt.StandbyDevices(self._cecid_sound)
        ret = self.cecadapt.StandbyDevices(self._cecid_fire)
        #self.sendiCecKlavo(0x10,0x6c);
        #self.sendiCecKlavo(self._cecid_sound,0x6c);
        #self.sendiCecKlavo(self._cecid_fire,0x6c);
        #self.sendiKlavo("223");


    def info(self):
        self.sendiCecKlavo(self._cecid_fire,0x35);
        
    def stop(self):
        self.sendiCecKlavo(self._cecid_fire,0x64);
        
    def rewind(self):
        self.sendiCecKlavo(self._cecid_fire,0x48);
        
    def fastforward(self):
        self.sendiCecKlavo(self._cecid_fire,0x49);
        
    def forward(self):
        self.sendiCecKlavo(self._cecid_fire,0x4b);
        
    def backward(self):
        self.sendiCecKlavo(self._cecid_fire,0x4c);
        
    def channels(self):
        self.sendiCecKlavo(self._cecid_fire,0x32);
        
    def klavo_alta(self):
        self.sendiCecKlavo(self._cecid_fire,0x01);
        #self.sendiKlavo("19");
        
    def klavo_basa(self):
        self.sendiCecKlavo(self._cecid_fire,0x02);
        #self.sendiKlavo("20");
        
    def klavo_maldekstra(self):
        self.sendiCecKlavo(self._cecid_fire,0x03);
        #self.sendiKlavo("21");
        
    def klavo_dekstra(self):
        self.sendiCecKlavo(self._cecid_fire,0x04);
        #self.sendiKlavo("22");
        
    def klavo_OK(self):
        self.sendiCecKlavo(self._cecid_fire,0x00);
        #self.sendiKlavo("66");
        

    def klavo_menuo(self):
        self.sendiCecKlavo(self._cecid_fire,0x0b);
        #self.sendiKlavo("82");

    def klavo_reen(self):
        self.sendiCecKlavo(self._cecid_fire,0x0d);
        #self.sendiKlavo("4");

    def klavo_hejmo(self):
        self.sendiCecKlavo(self._cecid_fire,0x09);
        #self.sendiKlavo("3");

    def klavo_ludi_pauzi(self):
        # pause
        self.sendiCecKlavo(self._cecid_fire,0x46);
        # play
        #self.sendiCecKlavo(self._cecid_fire,0x46);

    def klavo_sekva_kanalo(self):
        self.sendiCecKlavo(self._cecid_fire,0x30);
        #self.sendiKlavo("87");

    def klavo_antaua_kanalo(self):
        self.sendiCecKlavo(self._cecid_fire,0x31);
        #self.sendiKlavo("88");

    def VolumoSupren(self):
        self.sendiCecKlavo(self._cecid_sound,0x41);

    def VolumoMalsupren(self):
        self.sendiCecKlavo(self._cecid_sound,0x42);

    def Muta(self):
        self.sendiCecKlavo(self._cecid_sound,0x43);

    def legi_apo_aktualan(self):
        self.konekti();
        line = self._device.shell("dumpsys window windows | grep mCurrentFocus");
        #self.malkonekti();
        return line;
        #self.applis_encours=[line.strip().rsplit(' ', 1)[-1] for line in ps.splitlines() if line.strip()]
        
