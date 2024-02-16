#include <EEPROM.h>
#include "GravityTDS.h"
#include <OneWire.h> 
#include <DallasTemperature.h>
#include <SoftwareSerial.h>


#define ONE_WIRE_BUS 7
#define TdsSensorPin A1

OneWire oneWire(ONE_WIRE_BUS); 
GravityTDS gravityTds;

DallasTemperature sensors(&oneWire);

SoftwareSerial s(10,11);
 
float tdsValue = 0;

#define SensorPin A0            //pH meter Analog output to Arduino Analog Input 0
#define Offset 0.00            //deviation compensate
#define LED 13
#define samplingInterval 20
#define printInterval 800
#define ArrayLenth  40    //times of collection
int pHArray[ArrayLenth];   //Store the average value of the sensor feedback
int pHArrayIndex=0;

float ph, wt, ec;

void setup(void)
{
  pinMode(LED,OUTPUT);
  Serial.begin(115200);
  s.begin(9600);
  Serial.println("Experiment time!");    //Test the serial monitor 
  
  sensors.begin();
  gravityTds.setPin(TdsSensorPin);
  gravityTds.setAref(5.0);  //reference voltage on ADC, default 5.0V on Arduino UNO
  gravityTds.setAdcRange(1024);  //1024 for 10bit ADC;4096 for 12bit ADC
  gravityTds.begin();  //initialization
}
void loop(void)
{
 sensors.requestTemperatures();
//    gravityTds.setTemperature(sensors.getTempCByIndex(0));  // set the temperature and execute temperature compensation
//    gravityTds.update();  //sample and calculate
//    tdsValue = gravityTds.getTdsValue();  // then get the value

  float rawEc = analogRead(TdsSensorPin) * 4.3 / 1024.0;
  float temperatureCoefficient = 1.0 + 0.02 * (sensors.getTempCByIndex(0) - 25.0);
  tdsValue = (rawEc / temperatureCoefficient) * 1;
  
  static unsigned long samplingTime = millis();
  static unsigned long printTime = millis();
  static float pHValue,voltage;
  if(millis()-samplingTime > samplingInterval)
  {
      pHArray[pHArrayIndex++]=analogRead(SensorPin);
      if(pHArrayIndex==ArrayLenth)pHArrayIndex=0;
      voltage = avergearray(pHArray, ArrayLenth)*5.0/1024;
      pHValue = 3.5*voltage+Offset;
      samplingTime=millis();
  }
  if(millis() - printTime > printInterval)   //Every 800 milliseconds, print a numerical, convert the state of the LED indicator
  {
//    Serial.print("EC: ");
//        Serial.print(tdsValue,2);
//    Serial.print("    Temperature: "); 
//        Serial.print(sensors.getTempCByIndex(0));
//    Serial.print("    Voltage: ");
//        Serial.print(voltage,2);
//        Serial.print("    pH value: ");
//    Serial.println(pHValue,2);
//        digitalWrite(LED,digitalRead(LED)^1);
//        printTime=millis();

    ec = tdsValue;
    wt = sensors.getTempCByIndex(0);
    ph = pHValue;

//    Serial.print(ph, 2); Serial.print("A");
//    Serial.print(wt); Serial.print("B");
//    Serial.print(ec, 2); Serial.print("C");

      s.print(ph, 2); s.print("A");
      s.print(wt); s.print("B");
      s.print(ec, 2); s.print("C");
      s.print("\n");
    delay(10000);

  }
}
double avergearray(int* arr, int number){
  int i;
  int max,min;
  double avg;
  long amount=0;
  if(number<=0){
    Serial.println("Error number for the array to avraging!/n");
    return 0;
  }
  if(number<5){   //less than 5, calculated directly statistics
    for(i=0;i<number;i++){
      amount+=arr[i];
    }
    avg = amount/number;
    return avg;
  }else{
    if(arr[0]<arr[1]){
      min = arr[0];max=arr[1];
    }
    else{
      min=arr[1];max=arr[0];
    }
    for(i=2;i<number;i++){
      if(arr[i]<min){
        amount+=min;        //arr<min
        min=arr[i];
      }else {
        if(arr[i]>max){
          amount+=max;    //arr>max
          max=arr[i];
        }else{
          amount+=arr[i]; //min<=arr<=max
        }
      }//if
    }//for
    avg = (double)amount/(number-2);
  }//if
  return avg;
    //temperature = readTemperature();  //add your temperature sensor and read it
//  sensors.requestTemperatures();
//  float rawEc = analogRead(pin::tds_sensor) * 4.3 / 1024.0; // read the analog value more stable by the median filtering algorithm, and convert to voltage value
//  float temperatureCoefficient = 1.0 + 0.02 * (sensors.getTempCByIndex(0) - 25.0); // temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0));
//  tdsValue = (rawEc / temperatureCoefficient) * 1; // temperature and calibration compensation
//  Serial.print(F("EC:")); Serial.println(tdsValue, 2);
}
