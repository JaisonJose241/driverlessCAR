# importing the requests library
import requests
import pygame

flag = 0

def init():
    pygame.init()
    win = pygame.display.set_mode((100,100))
 
def getKey(keyName):
    ans = False
    for eve in pygame.event.get():pass
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame,'K_{}'.format(keyName))
    if keyInput [myKey]:
        ans = True
    pygame.display.update()
 
    return ans

 
if __name__ == '__main__':
    init()
    while True:
        if getKey('LEFT'):
            print('Key Left was pressed')
            if flag == 0:
                r = requests.get(url = "http://192.168.0.125/2-1-100-1000")
            flag=1    

        elif getKey('RIGHT'):
            print('Key Right was pressed')
            if flag == 0:
                r = requests.get(url = "http://192.168.0.125/1-2-1000-1000")
            flag=1   
            
        elif getKey('UP'):
            print('Key up was pressed')
            if flag == 0:
                r = requests.get(url = "http://192.168.0.125/1-1-1000-1000")
            flag=1   

        elif getKey('DOWN'):
            print('Key down was pressed') 
            if flag == 0:
                r = requests.get(url = "http://192.168.0.125/2-2-700-79")
            flag=1   

        elif getKey('q'):
            print("q is pressed")
            r = requests.get(url = "http://192.168.0.125/0-0-0-0")       
        else:
            if flag == 1:
                print("STOP") 
                r = requests.get(url = "http://192.168.0.125/stop")   
                flag = 0