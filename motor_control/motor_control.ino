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
  int timerIndex;
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

void initTimers(Motor m1, Motor m2) {
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 65536 - m1.waitCycles;  // set counter till ISR
  TCCR1B = 0;
  TCCR1B |= (1 << CS10) | (1 << CS11);  // prescale
  TIMSK1 |= (1 << TOIE1); // enable timer overflow interrupt

  TCCR2A = 0;
  TCCR2B = 0;
  TCNT2 = 256 - m2.waitCycles;
  TCCR2B = 0;
  TCCR2B |= (1 << CS10) | (1 << CS12); // 1024
  TIMSK2 |= (1 << TOIE1);
};

void applyPrescale(int timerIndex, int prescale) {
  if (timerIndex == 1) {
    int setting = 5;
    switch (prescale) {
      case 1: { setting = 1; } break;
      case 8: { setting = 2; } break;
      case 64: { setting = 3; } break;
      case 256: { setting = 4; } break;
      case 1024: { setting = 5; } break;
    }
    TCCR1B = (TCCR1B & 0b11111000) | setting;
  } else {
    int setting = 7;
    switch (prescale) {
      case 1: { setting = 1; } break;
      case 8: { setting = 2; } break;
      case 32: { setting = 3; } break;
      case 64: { setting = 4; } break;
      case 128: { setting = 5; } break;
      case 256: { setting = 6; } break;
      case 1024: { setting = 7; } break;
    }
    TCCR2B = (TCCR2B & 0b11111000) | setting;
  }
};

int getBestPossiblePrescale(int timerIndex, float idealPrescale) {
  if (timerIndex == 1) {
    if (256 <= idealPrescale) {
      return 1024;
    }
    if (64 <= idealPrescale && idealPrescale < 256) {
      return 256;
    }
    if (8 <= idealPrescale && idealPrescale < 64) {
      return 64;
    }
    if (1 <= idealPrescale && idealPrescale < 8) {
      return 8;
    }
    if (idealPrescale < 1) {
      return 1;
    }
  } else {
    if (256 <= idealPrescale) {
      return 1024;
    }
    if (128 <= idealPrescale && idealPrescale < 256) {
      return 256;
    }
    if (64 <= idealPrescale && idealPrescale < 128) {
      return 128;
    }
    if (32 <= idealPrescale && idealPrescale < 64) {
      return 64;
    }
    if (8 <= idealPrescale && idealPrescale < 32) {
      return 32;
    }
    if (1 <= idealPrescale && idealPrescale < 8) {
      return 8;
    }
    if (idealPrescale < 1) {
      return 1;
    }
  }
  
  return 1024;
}

void setMotorSpeed(Motor& m, float revsPerSec) {

  Serial.print("\nselected motor speed: ");
  Serial.print(revsPerSec);

  const float cpuFrequency = 16000000.0; // arduino constant  
  const float ticksPerMicrostep = 2.0;   // we toggle high/low in our ISR
  const float microstepsPerStep = float(m.microsteps);
  const float stepsPerRev = 200.0;

  float ticksPerSec = ticksPerMicrostep * microstepsPerStep * stepsPerRev * revsPerSec;

  // top speed: 1 rev/sec
  if (ticksPerSec > 6400) {
    Serial.print("\nTOO fast! Limiting speed.");
    ticksPerSec = 6400;
  }
  Serial.print("\nTicks per sec: ");
  Serial.print(ticksPerSec);

  float clockCyclesPerTick = cpuFrequency / ticksPerSec;

  float maxTimerCycles = m.timerIndex == 1 ? 65536 : 256;
  float idealPrescale = clockCyclesPerTick / maxTimerCycles;
  int prescale = getBestPossiblePrescale(m.timerIndex, idealPrescale);
  long waitCycles = long(clockCyclesPerTick / prescale);

  if (waitCycles < 16) {
    Serial.print("\nTOO few wait cycles! Setting a lower bound.");
    waitCycles = 16;
  }
  if (waitCycles >= maxTimerCycles) {
    Serial.print("\nTOO many wait cycles! Setting an upper bound.");
    waitCycles = maxTimerCycles;
  }  

  Serial.print("\nwait cycles: ");
  Serial.print(waitCycles);
  Serial.print("\nprescale: ");
  Serial.print(prescale);

  m.waitCycles = waitCycles;
  applyPrescale(m.timerIndex, prescale);
};

Motor m1 = { 3, 4, 6, 5, 7, LOW, 1024, 16, 255, 1 };
Motor m2 = { 8, 9, 11, 10, 12, LOW, 1024, 16, 255, 2 };

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

  setMotorSpeed(m1, 1.0);
  setMotorSpeed(m2, 1.0);
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
