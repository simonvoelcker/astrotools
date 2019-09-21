
const int dirPin1 = 3; 
const int stepPin1 = 4; 

const int microsteps1Pin1 = 6;
const int microsteps2Pin1 = 5;
const int enablePin1 = 7;

const int dirPin2 = 8; 
const int stepPin2 = 9; 

const int microsteps1Pin2 = 11;
const int microsteps2Pin2 = 10;
const int enablePin2 = 12;

int stepPinState1 = LOW;
int stepPinState2 = LOW;

const long cpuFrequency = 16000000; // arduino constant
const long cyclesPerTick = 64;      // prescale
const long ticksPerMicrostep = 2;   // we toggle high/low in our ISR
const long microstepsPerStep = 8;   // configured on the motor driver
const long stepsPerRev = 200;       // motor constant

const long secondsPerRev = 10;       // speed setting

long waitCycles1 = secondsPerRev * cpuFrequency / (cyclesPerTick * ticksPerMicrostep * microstepsPerStep * stepsPerRev);
long waitCycles2 = waitCycles1;

void setup() {

  Serial.begin(9600);  
  Serial.setTimeout(1000);

  pinMode(stepPin1, OUTPUT); 
  pinMode(stepPin2, OUTPUT); 
  pinMode(dirPin1, OUTPUT);
  pinMode(dirPin2, OUTPUT);

  pinMode(microsteps1Pin1, OUTPUT);
  pinMode(microsteps1Pin2, OUTPUT);
  pinMode(microsteps2Pin1, OUTPUT);
  pinMode(microsteps2Pin2, OUTPUT);
  pinMode(enablePin1, OUTPUT);
  pinMode(enablePin2, OUTPUT);

  digitalWrite(enablePin1, LOW); // low is enable
  digitalWrite(enablePin2, LOW); // low is enable

  // microsteps: 8
  digitalWrite(microsteps1Pin1, LOW);
  digitalWrite(microsteps2Pin1, LOW);
  digitalWrite(microsteps1Pin2, LOW);
  digitalWrite(microsteps2Pin2, LOW);
  
  digitalWrite(dirPin1, HIGH); // low is clockwise
  digitalWrite(dirPin2, HIGH); // low is clockwise

  noInterrupts();
  TCCR1A = 0;
  TCCR1B = 0;
  // set counter till ISR
  TCNT1 = 65536 - waitCycles1;
  // prescale: 64
  TCCR1B |= (1 << CS10) | (1 << CS11);
  // enable timer overflow interrupt
  TIMSK1 |= (1 << TOIE1);
  interrupts();
}


ISR(TIMER1_OVF_vect)        
{
  // reset counter till next ISR
  TCNT1 = 65536 - waitCycles1;
  // toggle step pin
  stepPinState1 = stepPinState1 == LOW ? HIGH : LOW;
  digitalWrite(stepPin1, stepPinState1);
  digitalWrite(stepPin2, stepPinState1);
}


void loop() {
  long num = Serial.parseInt();
  if (num != 0) {
    Serial.print("Setting delay.\n");
    waitCycles1 = num;
  }
}
