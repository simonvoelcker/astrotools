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

void setMotorState(Motor m, bool enable, bool clockWise) {
  digitalWrite(m.enablePin, enable ? LOW : HIGH); // low is enable
  digitalWrite(m.directionPin, clockWise ? LOW : HIGH); // low is clockwise
  digitalWrite(m.microstepsPin1, m.microsteps == 2 || m.microsteps == 16 ? HIGH : LOW);
  digitalWrite(m.microstepsPin2, m.microsteps == 4 || m.microsteps == 16 ? HIGH : LOW);
};

// TODO actually apply prescale based on configured value

void initTimers(Motor m1, Motor m2) {
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 65536 - m1.waitCycles;  // set counter till ISR
  TCCR1B |= (1 << CS10) | (1 << CS11);  // prescale
  TIMSK1 |= (1 << TOIE1); // enable timer overflow interrupt

  TCCR2A = 0;
  TCCR2B = 0;
  TCNT2 = 256 - m2.waitCycles;
  TCCR2B |= (1 << CS10) | (1 << CS12); // 1024
  TIMSK2 |= (1 << TOIE1);
};

void setMotorSpeed(Motor& m, float revsPerSec) {
  
  const float cpuFrequency = 16000000.0; // arduino constant
  const float cyclesPerTick = float(m.prescale);
  const float ticksPerMicrostep = 2.0;   // we toggle high/low in our ISR
  const float microstepsPerStep = float(m.microsteps);
  const float stepsPerRev = 200.0;

  const long waitCycles = long(cpuFrequency / (cyclesPerTick * ticksPerMicrostep * microstepsPerStep * stepsPerRev * revsPerSec));

  Serial.print(waitCycles);

  if (waitCycles < 50) {
    m.waitCycles = 50;
  } else if (waitCycles < 256) {
    m.waitCycles = waitCycles;
  } else {
    m.waitCycles = 255;
  }  
};

Motor m1 = { 3, 4, 6, 5, 7, LOW, 64, 8, 255 };
Motor m2 = { 8, 9, 11, 10, 12, LOW, 1024, 16, 255 };

void setup() {

  Serial.begin(9600);  
  Serial.setTimeout(1000);

  initMotor(m1);
  initMotor(m2);

  setMotorState(m1, true, false);
  setMotorState(m2, true, false);

  noInterrupts();
  initTimers(m1, m2);
  interrupts();

  setMotorSpeed(m1, 0.1);
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
