import kivy
from kivy.app import App
from kivy.uix.carousel import Carousel

kivy.require('1.9.0')
from kivy.uix.image import AsyncImage,Image
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.scatter import Scatter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
#from SensorDispatcher import SensorSubscriber
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

with PyCallGraph(output=GraphvizOutput()):
    code_to_profile()

import time
import json
import os
import json
from pprint import pprint
from kivy.core.window import Window

from subprocess import check_output
#from PIL import image

now = time.time()

class SensorManager(FloatLayout):
 
     
    def __init__(self, **kwargs):
        self.showMeasurements=False #true-> shows gyro and acceleration false -> show gauge
		
        super(SensorManager,self).__init__(**kwargs)
        sensorSubscriber = SensorSubscriber()
        self.jsonVar = sensorSubscriber.getDummyMsg()
        sensorSubscriber.setMsgCallBackFcn(self.callBackFnct)
        self.label = Label()
        self.add_widget(self.label)

        self.opfer=time.time()
        self.updateLabel()
        
        self.cadran=Image(source="cadran.png",size_hint=(0,0))
        
        self.add_widget(self.cadran)
        
        self.upsidedown=Image(source="upsidedowncar.jpg",size_hint=(0,0))
        
        self.add_widget(self.upsidedown)
        
        self.lowbattery=Image(source="lowbattery.jpg",size_hint=(0,0))
        self.add_widget(self.lowbattery)
        
        self.widgetSize=Window.size
        self.container = Scatter(size=self.widgetSize)
        self.needle=Image(source="needle.png",size=(0,0))
        self.container.add_widget(self.needle)
        self.add_widget(self.container)
        
        self.colorflag=1
        
    def redGreenAlternate(self):
        self.colorflag=1-self.colorflag
        return [self.colorflag,1-self.colorflag,0,1]
        
    	        
    
    def sensorValues(self, sensor):
        self.setSizesToZero([self.upsidedown])
        #self.upsidedown.size_hint=(0,0)
        sign = 'Acceleration:'
        sign2 = 'Gyroscope:'
        info = BoxLayout(orientation='vertical', spacing=2)
        labelText = sign + "\nx:"+str(round(sensor['acceleration'][0]/800*9.81,4)) +\
                           "\ny:"+str(round(sensor['acceleration'][1]/800*9.81,4)) +\
                           "\nz:"+str(round(sensor['acceleration'][2]/800*9.81,4)) +\
                           '\n' +sign2 +\
                           "\ngyro x:"+str(round(sensor['gyro'][0],4)) +\
                           "\ngyro y:"+str(round(sensor['gyro'][1],4)) +\
                           "\ngyro z:"+str(round(sensor['gyro'][2],4))+\
                           "\ndate: "+time.strftime("%d.%m.%Y")+\
                           "\ntime: "+time.strftime("%H:%M:%S")
                            
                           #"\ncommpass:"+str(sensor['compass_degrees']) 
        self.label.font_size=25
        self.label.pos_hint={"y":.2}
        self.label.color=[1,1,1,1]
        self.label.text = labelText
    
    def setSizesToZero(self,widgets):
        for w in widgets:
            w.size=(0,0)
            w.size_hint=(0,0)
	
    def show_ip(self):
        self.label.text="ipadress: "+check_output(['hostname','-I']).decode('utf-8')
        self.label.font_size=50
        
    def lowVoltage(self):
        self.setSizesToZero([self.cadran,self.container,self.upsidedown])
        self.label.text="Low Voltage!!!!!!!"
        self.label.font_size=100
        self.label.pos_hint={"x":0,"y":-.3}
        self.label.color=self.redGreenAlternate()

        self.lowbattery.size_hint=(1,.9)
        self.lowbattery.pos_hint={"x":0,"y":.3}
        
    def tilted(self):
        self.setSizesToZero([self.cadran,self.needle])
        self.label.text="Bitte Fahrzeug ausrichten"
        self.label.font_size=60
        self.label.pos_hint={"x":0,"y":-.2}
        self.label.color=self.redGreenAlternate()
        
        self.upsidedown.size_hint=(1,.75)
        self.upsidedown.pos_hint={"x":0.0,"y":0.4}
        
        
    def showGauge(self):
        self.label.text=""
        self.setSizesToZero([self.upsidedown])
        self.cadran.size_hint=(1,1)
        self.needle.size=self.widgetSize
        self.rotateNeedle(int(time.time())%21*5)
        
    def rotateNeedle(self,speed):
        minValue=0
        maxValue=100
        self.add_widget(Label(text=str(minValue),pos_hint={"x":-.4}))
        if speed<minValue or speed>maxValue:
            raise ValueError("can only display values between {} and {}",minValue, maxValue)
        self.container.size=Window.size
        self.container.rotation=speed/(maxValue-minValue)*180-90
    
        
    def updateLabel(self):
        #self.img.reload()
        sensor = self.getJsonDict()
        #print(sensor)
        print(os.popen("vcgencmd get_throttled").readline().replace("throttled=0x",""),end='')
        if time.time()<self.opfer+2:
            self.show_ip()
        elif "50005" in os.popen("vcgencmd get_throttled").readline():
            self.lowVoltage()
        elif sensor['acceleration'][2]/800*9.81<8:
            self.tilted()
        elif self.showMeasurements:
            self.sensorValues(sensor)
        else:
            self.showGauge()
            
    def callBackFnct(self,msg):
            self.jsonVar = msg.payload.decode()
            self.updateLabel()
        
    def getJsonDict(self):
        return json.loads(self.jsonVar)

       

class CarouselApp(App):
    def build(self):
        return SensorManager()
        
 
 
if __name__=="__main__":
    #Window.fullscreen = True
    CarouselApp().run()
    
