struct Motor {
  int directionPin; 
  int stepPin;
  int microstepsPin1;
  int microstepsPin2;
  int enablePin;

  int stepPinState;
  int prescale;
  int microsteps;
  int waitCycles;
};

void initMotor(Motor m) {
  pinMode(m.directionPin, OUTPUT);
  pinMode(m.stepPin, OUTPUT);
  pinMode(m.microstepsPin1, OUTPUT);
  pinMode(m.microstepsPin2, OUTPUT);
  pinMode(m.enablePin, OUTPUT);
};

void setMotorState(Motor m, bool enable, bool clockWise, int microsteps) {
  digitalWrite(m.enablePin, enable ? LOW : HIGH); // low is enable
  digitalWrite(m.directionPin, clockWise ? LOW : HIGH); // low is clockwise
  digitalWrite(m.microstepsPin1, microsteps == 2 || microsteps == 16 ? HIGH : LOW);
  digitalWrite(m.microstepsPin2, microsteps == 4 || microsteps == 16 ? HIGH : LOW);
};

void initTimers(Motor m1, Motor m2) {
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 65536 - m1.waitCycles;  // set counter till ISR
  TCCR1B |= (1 << CS10) | (1 << CS11);  // prescale
  TIMSK1 |= (1 << TOIE1); // enable timer overflow interrupt

  TCCR2A = 0;
  TCCR2B = 0;
  TCNT2 = 256 - m2.waitCycles;
  TCCR2B |= (1 << CS10) | (1 << CS12);
  TIMSK2 |= (1 << TOIE1);
};

Motor m1 = { 3, 4, 6, 5, 7, LOW, 1024, 16, 255 };
Motor m2 = { 8, 9, 11, 10, 12, LOW, 1024, 16, 255 };

const long cpuFrequency = 16000000; // arduino constant
const long cyclesPerTick = 64;      // prescale
const long ticksPerMicrostep = 2;   // we toggle high/low in our ISR
const long microstepsPerStep = 8;   // configured on the motor driver
const long stepsPerRev = 200;       // motor constant

const long secondsPerRev = 10;       // speed setting

// m1.waitCycles = secondsPerRev * cpuFrequency / (cyclesPerTick * ticksPerMicrostep * microstepsPerStep * stepsPerRev);
// m2.waitCycles = 200;

void setup() {

  Serial.begin(9600);  
  Serial.setTimeout(1000);

  initMotor(m1);
  initMotor(m2);

  setMotorState(m1, true, false, 8);
  setMotorState(m2, true, false, 16);

  noInterrupts();
  initTimers(m1, m2);
  interrupts();
}

ISR(TIMER1_OVF_vect)        
{
  // reset counter till next ISR
  TCNT1 = 65536 - m1.waitCycles;
  // toggle step pin
  m1.stepPinState = m1.stepPinState == LOW ? HIGH : LOW;
  digitalWrite(m1.stepPin, m1.stepPinState);
}

ISR(TIMER2_OVF_vect)        
{
  // reset counter till next ISR
  TCNT2 = 256 - m2.waitCycles;
  // toggle step pin
  m2.stepPinState = m2.stepPinState == LOW ? HIGH : LOW;
  digitalWrite(m2.stepPin, m2.stepPinState);
}

void loop() {
  long num = Serial.parseInt();
  if (num != 0) {
    Serial.print("Setting delay.\n");
    m1.waitCycles = num;
  }
}
