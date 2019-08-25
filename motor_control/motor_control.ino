// defines pins numbers
const int dirPin = 5; 
const int stepPin = 6; 

const int microsteps1Pin = 11;
const int microsteps2Pin = 10;
const int enablePin = 12;

int stepPinState = LOW;

const long cpuFrequency = 16000000; // arduino constant
const long cyclesPerTick = 64;      // prescale
const long ticksPerMicrostep = 2;   // we toggle high/low in our ISR
const long microstepsPerStep = 8;   // configured on the motor driver
const long stepsPerRev = 200;       // motor constant

const long secondsPerRev = 4;       // speed setting

long waitCycles =  secondsPerRev * cpuFrequency / (cyclesPerTick * ticksPerMicrostep * microstepsPerStep * stepsPerRev);


void setup() {

  Serial.begin(9600);  
  Serial.setTimeout(1000);

  pinMode(stepPin, OUTPUT); 
  pinMode(dirPin, OUTPUT);

  pinMode(microsteps1Pin, OUTPUT);
  pinMode(microsteps2Pin, OUTPUT);
  pinMode(enablePin, OUTPUT);

  digitalWrite(enablePin, LOW); // low is enable

  // microsteps: 8
  digitalWrite(microsteps1Pin, LOW);
  digitalWrite(microsteps2Pin, LOW);
  
  digitalWrite(dirPin, HIGH); // low is clockwise

  noInterrupts();
  TCCR1A = 0;
  TCCR1B = 0;

  // set counter till ISR
  TCNT1 = 65536 - waitCycles;

  // prescale: 64
  TCCR1B |= (1 << CS10) | (1 << CS11);

  // enable timer overflow interrupt
  TIMSK1 |= (1 << TOIE1);
  interrupts();
}


ISR(TIMER1_OVF_vect)        
{
  // reset counter till next ISR
  TCNT1 = 65536 - waitCycles;
  // toggle step pin
  stepPinState = stepPinState == LOW ? HIGH : LOW;
  digitalWrite(stepPin, stepPinState);
}


void loop() {
  long num = Serial.parseInt();
  if (num != 0) {
    Serial.print("Setting delay.\n");
    waitCycles = num;
  }
}
