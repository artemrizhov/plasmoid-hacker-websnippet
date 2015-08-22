# -*- coding: utf-8 -*-
import json
import os
import re
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *


DEFAULT_URL = ('https://github.com/artemrizhov/plasmoid-hacker-websnippet'
               '#hacker-websnippet-plasmoid')


class HackerWebSnippet(plasmascript.Applet):
    def __init__(self, parent, args=None):
        super(HackerWebSnippet, self).__init__(parent)
        self.url = DEFAULT_URL
        self.interval = 1

    def init(self):
        self.settings = self.config('General')
        self.readConfig()
        
        self.setHasConfigurationInterface(True)
        
        self.theme = Plasma.Svg(self)
        self.theme.setImagePath('widgets/background')
        self.setBackgroundHints(Plasma.Applet.DefaultBackground)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)

        self.webView = Plasma.WebView()
        self.connect(self.webView, SIGNAL('loadFinished(bool)'),
                     self.loadFinished)
        self.webView.setAutoFillBackground(True)
        self.webView.setUrl(KUrl(self.url))

        self.layout = QGraphicsLinearLayout(Qt.Horizontal, self.applet)
        self.layout.addItem(self.webView)
        self.setLayout(self.layout)

        self.timerid = self.startTimer(1000 * 60 * self.interval)

    def configChanged(self):
        self.readConfig()
        plasmascript.Applet.configChanged(self)

        if not self.url.startswith('http'):
            self.url = 'http://' + self.url
        else:
            pass
        print QVariant(QVariant(DEFAULT_URL)).toString()

        self.configOK()
        self.update()

    def readConfig(self):
        # The returning value type is not clear, so I've used QVariant wrapper
        # to be sure the toString() method will present on the value.
        self.url = str(QVariant(self.settings.readEntry(
            'url', DEFAULT_URL)).toString())
        self.interval, success = self.settings.readEntry(
            'interval', 1).toInt()
        self.custom_js = str(QVariant(self.settings.readEntry(
            'custom_js')).toString())

    def configOK(self):
        # Disable previous timer.
        if self.timerid:
            self.killTimer(self.timerid)
            self.timerid = None
        # If interval is not 0 then setup new timer.
        if self.interval:
            self.timerid = self.startTimer(1000 * 60 * self.interval)
        # Reload the page.
        self.webView.setUrl(KUrl(self.url))

    def reloadPage(self):
        self.webView.page().triggerAction(self.webView.page().Reload)

    def timerEvent(self, event):
        self.reloadPage()
        self.update()

    def loadFinished(self, success):
        if success:
            # Embed the specified javascript into the page.
            if self.custom_js.startswith('http:') or\
                    self.custom_js.startswith('https:'):
                js = '''
                    (function(){{
                        var script = document.createElement('script');
                        document.body.appendChild(script);
                        script.src = {};
                    }})();
                '''.format(json.dumps(self.custom_js))
            elif self.custom_js.startswith('file://'):
                with open(self.custom_js[len('file://'):], 'r') as f:
                    js = f.read()
            else:
                js = self.custom_js
                if js.startswith('javascript:'):
                    js = js[len('javascript:'):]
            if js:
                self.webView.mainFrame().evaluateJavaScript(QString(js))

def CreateApplet(parent):
    return HackerWebSnippet(parent)
