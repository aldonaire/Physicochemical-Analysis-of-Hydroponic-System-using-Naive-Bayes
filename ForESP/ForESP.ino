#include<SoftwareSerial.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
//#include <ArduinoJson.h>

WiFiClient wifiClient;
SoftwareSerial s (D1, D2);

const char* ssid = "WifiName";
const char* pass = "WifiPass";

char c;
String dataIn;
int8_t indexOfA, indexOfB, indexOfC;
String ph,wt,ec;

void setup() {
  Serial.begin(115200);
  s.begin(9600);
  WiFi.begin(ssid, pass);   //WiFi connection
//  while(!Serial) continue;
  
  while (WiFi.status() != WL_CONNECTED) {  //Wait for the WiFI connection completion
    delay(500);
    Serial.println("Waiting for connection");
  }


}

void loop() {
//  String msg = mySerial.readStringUntil('\r');
//  Serial.println(msg);

//    StaticJsonBuffer<1000> jsonBuffer;
//    JsonObject& root = jsonBuffer.parseObject(s);
//    if(root == JsonObject::invalid())
//      return;

//    String ph = root["ph"];
//    String wt = root["wt"];
//    String ec = root["ec"];
  while(s.available()>0){
    c=s.read();
    if(c=='\n'){break;}
    else{dataIn+=c;}
  }
    if(c=='\n'){
    Parse_the_Data();
    //changable name
    String flask_api = "http://nomorepaidwebsite.com/pred?ph="+ph+"&wt="+wt+"&ec="+ec;
    if (WiFi.status() == WL_CONNECTED) { //Check WiFi connection status
 
    HTTPClient http;    //Declare object of class HTTPClient
 
    http.begin(wifiClient, flask_api);      //Specify request destination
    http.addHeader("Content-Type", "text/plain");  //Specify content-type header
 
    int httpCode = http.POST("Message from ESP8266");   //Send the request
    String payload = http.getString();                  //Get the response payload
 
    Serial.println(httpCode);   //Print HTTP return code
    Serial.println(payload);    //Print request response payload
 
    http.end();  //Close connection
 
    } else {
   
      Serial.println("Error in WiFi connection");
   
    }
 
    delay(10000);
        c=0;
        dataIn="";
    }

}

void Parse_the_Data(){
  indexOfA = dataIn.indexOf("A");
  indexOfB = dataIn.indexOf("B");
  indexOfC = dataIn.indexOf("C");

  ph = dataIn.substring (0, indexOfA);
  wt = dataIn.substring (indexOfA+1, indexOfB);
  ec = dataIn.substring (indexOfB+1, indexOfC);
}
