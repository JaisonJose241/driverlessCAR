/* include library */
#include <ESP8266WiFi.h>
#include<string.h>
/* define port */
WiFiClient client;
WiFiServer server(80);

/* WIFI settings */
const char* ssid= "WIFI9891239479";//"bharti9198";
const char* password = "special321";

/* data received from application */
String data, eA, eB;
int enA, enB, index_A;

/* define L298N or L293D motor control pins */
int leftMotorForward = 4;     /* GPIO4(D2) -> IN3   *///1
int rightMotorForward = 15;   /* GPIO12(D6) -> IN1 *///3
int leftMotorBackward = 5;    /* GPIO5(D1) -> IN4  *///0
int rightMotorBackward = 13;  /* GPIO14(D5) -> IN2  *///2

int enableA = 14; //D7
int enableB = 12; // D8


void setup()
{
  /* initialize motor control pins as output */
  pinMode(leftMotorForward, OUTPUT);
  pinMode(rightMotorForward, OUTPUT); 
  pinMode(leftMotorBackward, OUTPUT);  
  pinMode(rightMotorBackward, OUTPUT);

  pinMode(enableA, OUTPUT);
  pinMode(enableB, OUTPUT);
  
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  while ((!(WiFi.status() == WL_CONNECTED)))
  {
    delay(1000);
    Serial.print(WiFi.status());
    Serial.println(WL_CONNECTED);
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("NodeMCU Local IP is : ");
  Serial.print((WiFi.localIP()));
  server.begin();

}

void loop()
{
    /* If the server available, run the "checkClient" function */  
    client = server.available();
    if (!client) return; 

    data = checkClient();
    String data_old = data;
    Serial.println(data);
    
    if ((data[0] == '1') && (data[2] == '1')){
      data = "forward";
    }
    else if ((data[0] == '2') && (data[2] == '2')){
      data = "backward";
    }
    else if ((data[0] == '2') && (data[2] == '1')){
      data = "left";
    }
    else if ((data[0] == '1') && (data[2] == '2')){
      data = "right";
    }
    else if ((data[0] == '0') && (data[2] == '0')){
      data = "stop";
    }
    
    for(int i = 4; i < 9; i++){
      if(data_old[i] == '-'){
        index_A = i;
        break;
      }
      else{
        eA = eA + String(data_old[i]);
      }
    }

    for(int i = index_A+1; i < 13; i++){
      if(data_old[i] == ' '){
        break;
      }
      else{
        eB = eB + String(data_old[i]);
      }
    }

    enA = eA.toInt();
    enB = eB.toInt();
    Serial.println(enA);
    Serial.println(enB);
    eA = "";
    eB = "";
    Serial.println(data);
/************************ Run function according to incoming data from application *************************/
    /* If the incoming data is "forward", run the "MotorForward" function */
    if (data == "forward") MotorForward();
    /* If the incoming data is "backward", run the "MotorBackward" function */
    else if (data == "backward") MotorBackward();
    /* If the incoming data is "left", run the "TurnLeft" function */
    else if (data == "left") TurnLeft();
    /* If the incoming data is "right", run the "TurnRight" function */
    else if (data == "right") TurnRight();
    /* If the incoming data is "stop", run the "MotorStop" function */
    else if (data == "stop") MotorStop();
} 

/********************************************* FORWARD *****************************************************/
void MotorForward(void)   
{
  
  analogWrite(enableA, enA);
  analogWrite(enableB, enB);
  digitalWrite(leftMotorForward,HIGH);
  digitalWrite(rightMotorForward,HIGH);
  digitalWrite(leftMotorBackward,LOW);
  digitalWrite(rightMotorBackward,LOW);
}

/********************************************* BACKWARD *****************************************************/
void MotorBackward(void)   
{
  
  analogWrite(enableA, enA);
  analogWrite(enableB, enB);
  digitalWrite(leftMotorBackward,HIGH);
  digitalWrite(rightMotorBackward,HIGH);
  digitalWrite(leftMotorForward,LOW);
  digitalWrite(rightMotorForward,LOW);
}

/********************************************* TURN LEFT *****************************************************/
void TurnLeft(void)   
{
  analogWrite(enableA, enA);
  analogWrite(enableB, enB);
  digitalWrite(leftMotorForward,LOW);
  digitalWrite(rightMotorForward,HIGH);
  digitalWrite(rightMotorBackward,LOW);
  digitalWrite(leftMotorBackward,HIGH);  
}

/********************************************* TURN RIGHT *****************************************************/
void TurnRight(void)   
{
  analogWrite(enableA, enA);
  analogWrite(enableB, enB);
  digitalWrite(leftMotorForward,HIGH);
  digitalWrite(rightMotorForward,LOW);
  digitalWrite(rightMotorBackward,HIGH);
  digitalWrite(leftMotorBackward,LOW);
}

/********************************************* STOP *****************************************************/
void MotorStop(void)   
{
  analogWrite(enableA, enA);
  analogWrite(enableB, enB);
  digitalWrite(leftMotorForward,LOW);
  digitalWrite(leftMotorBackward,LOW);
  digitalWrite(rightMotorForward,LOW);
  digitalWrite(rightMotorBackward,LOW);
}

String checkClient (void)
{
  while(!client.available()) delay(1); 
  String request = client.readStringUntil('\r');
  request.remove(0, 5);
  request.remove(request.length()-9,9);
  client.println("HTTP/1.1 200 OK");
  return request;
}
