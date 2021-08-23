#coding=utf-8
#qpy:kivy

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.uix.camera import Camera
from kivy.lang import Builder
import numpy as np
import cv2
import time
from kivy.clock import mainthread
from kivy.utils import platform
import threading

# check for type of device
if platform == 'android':
    from usb4a import usb
    from usbserial4a import serial4a
else:
    from serial.tools import list_ports
    from serial import Serial



Builder.load_file("main.kv")

frame = np.array([])
org_img = lane_img = img = frame
lines = []
##print(img.shape[1], img.shape[0])
select_img = 50
offset = 0    
roi_y1, roi_y2 = 0, 0



def ESP():
  global lines, org_img, lane_img, img, select_img, offset, roi_y1, roi_y2
  device_name_list = []
  if platform == 'android':
      usb_device_list = usb.get_usb_device_list()
      device_name_list = [ device.getDeviceName() for device in usb_device_list ]
  else:
      usb_device_list = list_ports.comports()
      device_name_list = [ port.device for port in usb_device_list ]  
  for device_name in device_name_list:
    pass
  if platform == 'android':
    device = usb.get_usb_device(device_name)
    if not device:
        raise SerialException("Device {} not present!".format(device_name))
    if not usb.has_usb_permission(device):
      usb.request_usb_permission(device)
      while usb.has_usb_permission(device):
        time.sleep(0.001)
        break  
    time.sleep(3) 
    serial_port = serial4a.get_serial_port(
        device_name,
        9600,
        8,
        'N',
        1,
        timeout=1)
  else:
      serial_port = Serial(
          device_name,
          9600,
          8,
          'N',
          1,
          timeout=1)       
  
  curve = 0
  while True: 
    if len(org_img) and len(img):
        #print(len(org_img))
        lane_left, lane_right = extract_single_lane(lines, org_img, roi_y1 + 10, roi_y2 - 10)

        if len(lane_left) == 0 and len(lane_right) > 0:           
            x2 = int((lane_right[0]+lane_right[2])/2)
            y2 = int((lane_right[1]+lane_right[3])/2)
            x1, y1 = 0, y2

        elif len(lane_right) == 0 and len(lane_left) > 0:
            x1 = int((lane_left[0]+lane_left[2])/2)
            y1 = int((lane_left[1]+lane_left[3])/2)
            x2, y2 = org_img.shape[1], y1

        elif len(lane_left) == 0 and len(lane_right) == 0:
            x1, y1, x2, y2 =  0, int(org_img.shape[0]/2), org_img.shape[1], int(org_img.shape[0]/2)            
            #print(org_img.shape[0])

        else:    
            x1 = int((lane_left[0]+lane_left[2])/2)
            y1 = int((lane_left[1]+lane_left[3])/2)
            x2 = int((lane_right[0]+lane_right[2])/2)
            y2 = int((lane_right[1]+lane_right[3])/2)

        lane_img = extrapolated_lanes_image(org_img, lines, roi_y1 + 10, roi_y2 - 10)


        x_mid_path = int((x2+x1)/2)
        x_mid_screen = int(img.shape[1]/2) + 40
        deviation = int(x_mid_path - x_mid_screen)
        deviation_display = int(deviation/(x_mid_screen/2) * 10)
        if abs(deviation_display) > 3:
            deviation_display = int((deviation_display/ abs(deviation_display)) * 3)

        #print(deviation_display)

        if deviation_display < 0:
            text = "left:  " + str(deviation_display)
        elif deviation_display > 0:
            text = "right:  " + str(deviation_display)
        else:
            text = "center"

        # cv2 draw on the image the overlay features
        cv2.line(lane_img, (x1, y1), (x2, y2), [255,0,0], 3)
        lane_img = cv2.circle(lane_img, (x_mid_path,100), radius=1, color=(0, 0, 255), thickness=18)
        lane_img = cv2.circle(lane_img, (x_mid_path,y1), radius=0, color=(0, 0, 255), thickness=17)
        #lane_img = cv2.circle(lane_img, (int(org_img.shape[0]/2), int(org_img.shape[1]/2)), radius=0, color=(0, 0, 255), thickness=17)
        cv2.line(lane_img, (x_mid_path, 100), (x_mid_screen, 100), (0,255,0), 3)
        cv2.putText(lane_img, text, (x_mid_screen - 100, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 2, cv2.LINE_AA)
        
        #if curve != deviation_display:
        curve = deviation_display

        left_PWM = 755
        right_PWM = 755
        tilt_speed = abs(curve*30)
        if curve == 0:        
            my_data = "2-2-"+ str(left_PWM) + "-" + str(right_PWM)    
        
        if curve < 0: #turn left     
            my_data = "2-2-" + str(550) + "-"  + str(right_PWM + tilt_speed) 
            
        if curve > 0:
            my_data = "2-2-" + str(left_PWM + tilt_speed) + "-" + str(550)

        data = bytes(my_data + "\n", 'utf8')
        
        #if serial_port.is_open:
        print(data)
        serial_port.write(data)  

        time.sleep(0.01) 

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
---------------------------------------------------------------------->>>>>>>>>>>>>>>
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def cv2_python(frame):
    global lines, org_img, lane_img, img, select_img, offset, roi_y1, roi_y2   
    frame1 = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE) 
    org_img = frame1   
    #print(org_img.shape[1])    
    roi_y1 = int(org_img.shape[0]/2) - select_img  - offset
    roi_y2 = int(org_img.shape[0]/2) + select_img  - offset              
    org_img = cv2.cvtColor(org_img, cv2.COLOR_BGR2RGB) # converts from BGR to RGB
    img = cv2.cvtColor(org_img, cv2.COLOR_RGB2GRAY) # converts from BGR to RGB
    cv2.GaussianBlur(img, (3, 3), 0)
    roi_vertices = np.array([[[org_img.shape[1],roi_y1], [0,roi_y1], [0,  roi_y2], [org_img.shape[1],  roi_y2]]])
    gray_select_roi = region_of_interest(img, roi_vertices)
    cannyed_image = cv2.Canny(gray_select_roi, 20, 140)
    lines = cv2.HoughLinesP(cannyed_image,
                            rho=6,
                            theta=np.pi / 60,
                            threshold=50,
                            lines=np.array([]),
                            minLineLength=30,
                            maxLineGap=50 )

    if len(lane_img) > 0:

        overlay_img = cv2.addWeighted(org_img, 0.8, lane_img, 1, 0)
        frame_rgb = overlay_img
    else:
        frame_rgb = org_img 
    return frame_rgb



#################################################################################
def region_of_interest(img, vertices):
    #defining a blank mask to start with
    mask = np.zeros_like(img)   
    #defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255       
    #filling pixels inside the polygon defined by "vertices" with the fill color    
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    #returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def draw_lines(img, lines, color=[255, 0, 0], thickness=2):
    if len(lines[0][0]) > 1:
        for line in lines:
            for x1,y1,x2,y2 in line:
                cv2.line(img, (x1, y1), (x2, y2), color, thickness)


def seperate_left_right(lines, img):
    lines_left = []
    lines_right = []
    if lines is not None:
        for line in lines:
            for x1,y1,x2,y2 in line:
                if y1 > y2: #positive slope
                    lines_left.append([x1, y1, x2, y2])
                elif y1 < y2: #negative slope
                    lines_right.append([x1, y1, x2, y2])
                #cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)    
    return lines_left, lines_right

def cal_avg_value(values):
    if not (type(values) == 'NoneType'):
        if len(values) > 0:
            cnt_values = len(values)
        else:
            cnt_values = 1
            values = [1]
        return sum(values) / cnt_values

def extrapolate_lines(lines, upper_border, lower_border):
    #TODO: use ROI polygon for extrapolating lines for further improvement
    # y = m*x+c
    
    #calulate average slope 'slope' and y-axis intersection 'c'
    slopes = []
    c_s = []
    
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            if x1 != x2:
                slope = (y1-y2)/(x1-x2)
                slopes.append(slope)
                c = y1 - slope * x1
                c_s.append(c)
    ##print(slopes)            
    avg_slope = cal_avg_value(slopes)
    avg_c = cal_avg_value(c_s)
    #calulate average intersection at lower_border
    x_lower_border_intersections = []
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            x_lower_border_intersection = (lower_border - avg_c) / avg_slope
            x_lower_border_intersections.append(x_lower_border_intersection)

    x_lane_lower_point = cal_avg_value(x_lower_border_intersections)
    x_lane_lower_point = int(x_lane_lower_point)
    
    #calulate average intersection at upper_border
    x_upper_border_intersections = []
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            x_upper_border_intersection = (upper_border - avg_c) / avg_slope
            x_upper_border_intersections.append(x_upper_border_intersection)
    x_lane_upper_point = int(cal_avg_value(x_upper_border_intersections))
    return [x_lane_lower_point, lower_border, x_lane_upper_point, upper_border]

def extract_single_lane(lines, img, upper_border, lower_border):
    lines_left, lines_right = seperate_left_right(lines, img) 
    lane_left = []
    lane_right = []
    if len(lines_left) > 1:
        lane_left = extrapolate_lines(lines_left, upper_border, lower_border)
    if len(lines_right) > 1:
        lane_right = extrapolate_lines(lines_right, upper_border, lower_border) 
    return lane_left, lane_right

def extrapolated_lanes_image(image, lines, roi_upper_border, roi_lower_border):
    lanes_img = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
    #print(lanes_img.shape)    
    lane_left, lane_right = extract_single_lane(lines, image, roi_upper_border, roi_lower_border)
    draw_lines(lanes_img, [[lane_left]], thickness=10)
    draw_lines(lanes_img, [[lane_right]], thickness=10)
    return lanes_img
############################################################################################
class AndroidCamera(Camera):
  camera_resolution =  (480, 360) #(640, 480) # (960, 720) 
  counter = 0

  def _camera_loaded(self, *largs):
    self.texture = Texture.create(size=self.camera_resolution, colorfmt='rgb') #np.flip(self.camera_resolution)
    #print(self.texture.size)
    self.texture_size = list(self.texture.size)

  def on_tex(self, *l):
    if self._camera._buffer is None:
        return None
    frame = self.frame_from_buf()
    self.frame_to_screen(frame)
    super(AndroidCamera, self).on_tex(*l)

  def frame_from_buf(self):
    w, h = self.resolution
    frame = np.frombuffer(self._camera._buffer.tostring(), 'uint8').reshape((h + h // 2, w)) #w,h
    frame_bgr = cv2.cvtColor(frame, 93)
    rrt = np.rot90(frame_bgr, 1)    
    return rrt 

  def frame_to_screen(self, frame):

    frame_rgb = cv2_python(frame)
    flipped = np.flip(frame_rgb, 0)
    buf = flipped.tostring()
    self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')


class MyLayout(BoxLayout):
  pass

class MyApp(App):
  def build(self):
    threading.Thread(target = ESP).start()   
    return MyLayout()

if __name__ == '__main__':
  MyApp().run()


