
#define HWSERIAL Serial5

const int ledPin = LED_BUILTIN;
static const int relay = 10;
static const int waterLevel = 14;

void setup() {
  Serial.begin(38400);
  HWSERIAL.begin(9600); 
  delay(50);
  pinMode(ledPin, OUTPUT);
  pinMode(relay, OUTPUT);
  pinMode(waterLevel, INPUT);
  digitalWrite(ledPin, HIGH);
  digitalWrite(relay, HIGH);
}

void loop() {

  //has the hub send us some input?
  //if a 1, that signifies that we should open the relay, turning on the attached device
  //if a 0, that signifies that we should close the relay, turning off the attached device
  if(HWSERIAL.available() == true)
  {
    char inByte = HWSERIAL.read();
    if(inByte == '0')
    {
      digitalWrite(ledPin, LOW);
      digitalWrite(relay, LOW);
    }
    else if(inByte == '1')
    {
      digitalWrite(ledPin, HIGH);
      digitalWrite(relay, HIGH);
    }
  }

  //continuously send out value of the contactless liquid sensor attached to the humidifier tank
  HWSERIAL.println(analogRead(waterLevel));
  Serial.println(analogRead(waterLevel));

  delay(1000); //power savings by only running the sensor program once a second
}
