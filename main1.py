import tkinter as tk
from PIL import Image,ImageTk
import firebase_admin
import RPi.GPIO as GPIO
from firebase_admin import credentials
from firebase_admin import db



class LightPhoto(tk.Canvas):
    def __init__(self,parent,state=False,**kwargs):
        super().__init__(parent,**kwargs)
        #建立圖片
        ##建立close的圖片
        close_image = Image.open('light_close.png')
        self.close_photo = ImageTk.PhotoImage(close_image)
        ##建立open的圖片
        open_image = Image.open('light_open.png')
        self.open_photo = ImageTk.PhotoImage(open_image)
        self.__state = None
        self.state = state
        #設canvas的寬高
        self.config(width=close_image.size[0]+20,height=close_image.size[1]+20)

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self,s):
        self.__state = s
        self.delete('all')
        if s == True:
            self.create_image(10,10,anchor=tk.NW,image=self.open_photo)
        else:
            self.create_image(10,10,anchor=tk.NW,image=self.close_photo)

class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        #建立firebase 連線
        cred = credentials.Certificate("private/raspberry1-4c914-firebase-adminsdk-hkne9-465e968baa.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://raspberry1-4c914-default-rtdb.firebaseio.com/'
        })

        led = db.reference('ledControl')       

        #建立title
        self.title("LED Controller")

        #建立按鈕

        self.lightPhoto = LightPhoto(self)
        self.lightPhoto.pack(padx=50,pady=30)
        currentState = led.get()['led']
        if currentState:
           self.lightPhoto.state = True
           GPIO.output(25,GPIO.HIGH)
        else:
           self.lightPhoto.state = False
           GPIO.output(25,GPIO.LOW)

        #註冊監聽
        #監聽必需在最後面
        led.listen(self.firebaseDataChange)
    #Firebase打true/false, 終端機出現: 資料內容:{'led': True} 資料路徑:/ 資料內容:False 資料路徑:/led
    def firebaseDataChange(self,event):
        print(f"資料內容:{event.data}")
        print(f"資料路徑:{event.path}")
        if event.path == "/":
            state = event.data['led']
        elif event.path ==  "/led":
            state = event.data
        
        if state:
            self.lightPhoto.state = True
            GPIO.output(25,GPIO.HIGH)
        else:
            self.lightPhoto.state = False
            GPIO.output(25,GPIO.LOW)

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(25,GPIO.OUT)
    window = Window()
    window.mainloop()

if __name__ == "__main__":
    main()