#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#       Fire TV Plugin
#       
"""
<plugin key="fire-tv" name="Amazon Fire TV (with Kodi remote)" author="jmichault" version="0.2" wikilink="https://github.com/jmichault/fire-tv" externallink="https://www.amazon.com/firetv">
 <description>
 </description>
  <params>
        <param field="Address" label="IP address" width="200px" required="true" default="192.168.1.191"/>
        <param field="Mode3" label="CEC ID for sound" width="200px" required="true" default="5"/>
        <param field="Mode4" label="CEC ID for Fire TV Stick" width="200px" required="true" default="11"/>
        <param field="Mode5" label="Update interval (sec)" width="30px" required="true" default="30"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
  </params>
</plugin>
"""
try:
    import Domoticz
except ImportError:
    import fakeDomoticz as Domoticz

import datetime
import gettext

if gettext.find('fire-tv',localedir='locale') != None:
    gettext.install('fire-tv',localedir='locale')
elif gettext.find('fire-tv',localedir='plugins/fire-tv/locale') != None:
    gettext.install('fire-tv',localedir='plugins/fire-tv/locale')

Domoticz.Log("FireTV "+ _("Ŝaltita"))

from firetv import FiretvRC

class BasePlugin:
    _tv = None
    _Address = None
    
    def onStart(self):
        global _tv
        global _Address
        
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()
        _Address = Parameters["Address"]
        _tv = FiretvRC( _Address ,int(Parameters["Mode3"]) ,int(Parameters["Mode4"]) )

        self.SourceOptions2 =   {   "LevelActions"  : "||||||",
                                    "LevelNames"    : "Off|"+_("Hejmo")+"|Netflix|Molotov|Kodi|Spotify",
                                    "LevelOffHidden": "true",
                                    "SelectorStyle" : "0"
                                }

        
        if len(Devices) == 0:
            Domoticz.Device(Name=_("Statuso"), Unit=1, Image=2, Type=17, Switchtype=17, Used=1).Create()
            Domoticz.Device(Name=_("Apo"), Unit=2, TypeName="Selector Switch", Switchtype=18, Image=2, Options=self.SourceOptions2, Used=1).Create()
        elif 1 not in Devices:
            Domoticz.Device(Name=_("Statuso"), Unit=1, Image=2, Type=17, Switchtype=17, Used=1).Create()
        elif 2 not in Devices:
            Domoticz.Device(Name=_("Apo"), Unit=2, TypeName="Selector Switch", Switchtype=18, Image=2, Options=self.SourceOptions2, Used=1).Create()

        
        # Set update interval, values below 10 seconds are not allowed due to timeout of 5 seconds in firetv.py script
        updateInterval = int(Parameters["Mode5"])
        if updateInterval < 30:
            if updateInterval < 10: updateInterval = 10
            Domoticz.Log("Update interval set to " + str(updateInterval) + " (minimum is 10 seconds)")
            Domoticz.Heartbeat(updateInterval)
        else:
            Domoticz.Heartbeat(30)

        return #--> return True
    
    # Executed each time we click on device through Domoticz GUI
    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log(_("onCommand alvokita por unuo ") + str(Unit) + _(": parametro '") + str(Command) + _("', nivelo: ") + str(Level))

        Command = Command.strip()
        action, sep, params = Command.partition(' ')
        action = action.capitalize()
        params = params.capitalize()
       
        if Unit == 1:   
                if action == "On":
                    Devices[1].Update(1, _("Ŝaltita"))
                    _tv.klavo_sxalti()
                elif action == "Off":
                    Devices[1].Update(0, _("Malŝaltita"))
                    UpdateDevice(2, 0, "0")
                    _tv.klavo_malsxalti()
                # klavoj de fora kontrolo
                elif Command == "Select": _tv.klavo_OK()
                elif Command == "Up": _tv.klavo_alta()
                elif Command == "Down": _tv.klavo_basa()
                elif Command == "Left": _tv.klavo_maldekstra()
                elif Command == "Right": _tv.klavo_dekstra()
                elif Command == "Home": _tv.klavo_hejmo()
                elif Command == "Back": _tv.klavo_reen()
                elif Command == "ContextMenu": _tv.klavo_menuo()
                elif Command == "PlayPause": _tv.klavo_ludi_pauzi()
                elif Command == "ChannelUp": _tv.klavo_sekva_kanalo()
                elif Command == "ChannelDown": _tv.klavo_antaua_kanalo()
                elif Command == "Info": _tv.info()
                #elif Command == "FullScreen": _tv.
                #elif Command == "ShowSubtitles": _tv.
                elif Command == "Stop": _tv.stop()
                elif Command == "BigStepBack": _tv.backward()
                elif Command == "Rewind": _tv.rewind()
                elif Command == "FastForward": _tv.fastforward()
                elif Command == "BigStepForward": _tv.forward()
                elif Command == "Channels": _tv.channels()
                elif Command == "VolumeUp": _tv.VolumoSupren()
                elif Command == "VolumeDown": _tv.VolumoMalsupren()
                elif Command == "Mute": _tv.Muta()
        elif Unit == 2:
                if Command == 'Set Level':
                    if Level == 10:			# Hejmo
                        _tv.apo("com.amazon.tv.launcher")
                    elif Level == 20:			# Netflix
                        _tv.apo("com.netflix.ninja")
                    elif Level == 30:			# Molotov
                        _tv.apo("tv.molotov.app")
                    elif Level == 40:			# Kodi
                        _tv.apo("org.xbmc.kodi")
                    elif Level == 50:			# Spotify
                        _tv.apo("com.spotify.tv.android")
                    UpdateDevice(2, 1, str(Level))

                    
        return

    # Execution depend of Domoticz.Heartbeat(x) x in seconds
    def onHeartbeat(self):
        tvStatus = None;
        fireApp = "";
        try:
            tvStatus = _tv.akiri_potencsxtato()
            Domoticz.Debug(_("Statuso")+" fireTV: " + str(tvStatus))
        except Exception as err:
            Domoticz.Log(_("adb ne konektita al fireTV (") +  str(err) + ")")
            del self._tv
            self._tv = FiretvRC( _Address , 5 , 11)
        if tvStatus == 'active':                        # TV is on
          Domoticz.Debug(" fireTV: dans active ")
          self.powerOn = True
          UpdateDevice(1, 1, _('fireTV aktiva')+fireApp)
          try:
            Domoticz.Debug(" fireTV: dans active,try ")
            longFireApp = _tv.legi_apo_aktualan()
            Domoticz.Debug(_("fireTV apo: ") + longFireApp)
            if longFireApp.find("netflix")>0:
                fireApp = _(",en ")+ "Netflix";
                UpdateDevice(2, 1, "20")
            elif longFireApp.find("molotov")>0:
                fireApp = _(",en ")+ "Molotov";
                UpdateDevice(2, 1, "30")
            elif longFireApp.find("kodi")>0:
                fireApp = _(",en ")+ "Kodi";
                UpdateDevice(2, 1, "40")
            elif longFireApp.find("spotify")>0:
                fireApp = _(",en ")+ "Spotify";
                UpdateDevice(2, 1, "50")
            elif longFireApp.find("PrimeVideo")>0:
                fireApp = _(",en ")+ "Prime";
                UpdateDevice(2, 1, "10")
            elif longFireApp.find("com.amazon.tv.launcher")>0:
                fireApp = _(",en Hejmo");
                UpdateDevice(2, 1, "10")
          except Exception as err:
            Domoticz.Log(_("adb(2) ne konektita al fireTV (") +  str(err) + ")")
        elif tvStatus == None:                        # TV is unknown
          Domoticz.Debug(_("Statuso fireTV: ") + str(tvStatus))
        else:                                           # TV is off or standby
          self.powerOn = False
          UpdateDevice(1, 0, 'off')
          UpdateDevice(2, 0, 'off')
        return

_plugin = BasePlugin()

def onStart():
    _plugin.onStart()

def onCommand(Unit, Command, Level, Hue):
    _plugin.onCommand(Unit, Command, Level, Hue)

def onHeartbeat():
    _plugin.onHeartbeat()

# Ĝisdatigu Aparato en datumbazon
def UpdateDevice(Unit, nValue, sValue, AlwaysUpdate=False):
    # Certigu, ke la aparato Domoticz ankoraŭ ekzistas (ĝi povas esti forigita) antaŭ ol ĝisdatigi ĝin
    if Unit in Devices:
        if ((Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (AlwaysUpdate == True)):
            Devices[Unit].Update(nValue, str(sValue))
            Domoticz.Log(_("ĝisdatigo ") + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
    return

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Nombro de aparatoj: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug(_("Aparato:             ") + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug(_("Interna ID:         '") + str(Devices[x].ID) + "'")
        Domoticz.Debug(_("Ekstera ID:         '") + str(Devices[x].DeviceID) + "'")
        Domoticz.Debug(_("Aparato Nomo:       '") + Devices[x].Name + "'")
        Domoticz.Debug(_("Aparato nValoro:     ") + str(Devices[x].nValue))
        Domoticz.Debug(_("Aparato sValoro:    '") + Devices[x].sValue + "'")
        Domoticz.Debug(_("Aparato LastaNivelo: ") + str(Devices[x].LastLevel))
    return
