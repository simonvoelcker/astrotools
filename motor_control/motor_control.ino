struct Motor {
  int directionPin; 
  int stepPin;
  int microstepsPin1;
  int microstepsPin2;
  int enablePin;

  int stepPinState;     // whether the step pin is high or low
  long prescale;        // arduino clock cycles before counting down a timer
  int microsteps;
  long waitCycles;
  long waitCyclesLeft;
  int timerIndex;
  
  long microstepCount;
  bool clockwise;

  float currentSpeed;
  float targetSpeed;
  float acceleration;
};

struct SimpleMotor {
  int directionPin;
  int stepPin;

  int stepPinState;
  int targetStepCount;      // target position to move to
};

// RA and Dec motors
Motor m1 = { 3, 4, 6, 5, 7, LOW, 1024, 16, 255, 255, 1, 0, false, 0.0, 0.0, 1.0 };
Motor m2 = { 8, 9, 11, 10, 12, LOW, 1024, 16, 255, 255, 2, 0, false, 0.0, 0.0, 1.0 };

// Focuser
SimpleMotor m3 = { 2, 13, LOW, 0 };

void initMotor(Motor m) {
  pinMode(m.directionPin, OUTPUT);
  pinMode(m.stepPin, OUTPUT);
  pinMode(m.microstepsPin1, OUTPUT);
  pinMode(m.microstepsPin2, OUTPUT);
  pinMode(m.enablePin, OUTPUT);

  digitalWrite(m.enablePin, HIGH); // high is disable
  digitalWrite(m.microstepsPin1, m.microsteps == 2 || m.microsteps == 16 ? HIGH : LOW);
  digitalWrite(m.microstepsPin2, m.microsteps == 4 || m.microsteps == 16 ? HIGH : LOW);
}

void initSimpleMotor(SimpleMotor m) {
  pinMode(m.directionPin, OUTPUT);
  pinMode(m.stepPin, OUTPUT);
}

void initTimers() {
  noInterrupts();

  // motor 1
  TCCR1A = 0;  // flags
  TCNT1 = 65535;  // set counter till ISR
  TCCR1B = (1 << CS10) | (1 << CS11);  // prescale

  // motor 2
  TCCR2A = 0;
  TCNT2 = 255;
  TCCR2B = (1 << CS10) | (1 << CS12);

  interrupts();
}

void setTimerEnabled(int timerIndex, bool enable) {
  if (timerIndex == 1) {
    if (enable) {
      TIMSK1 |= (1 << TOIE1);
    } else {
      TIMSK1 &= ~(1 << TOIE1);
    }
  } else {
    if (enable) {
      TIMSK2 |= (1 << TOIE1);
    } else {
      TIMSK2 &= ~(1 << TOIE1);
    }
  }
}

void applyPrescale(Motor& m, long prescale) {
  if (m.timerIndex == 1) {
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
  m.prescale = prescale;
}

long getBestPossiblePrescale(int timerIndex, float idealPrescale) {
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

  bool enable = revsPerSec != 0.0;
  digitalWrite(m.enablePin, enable ? LOW : HIGH);
  setTimerEnabled(m.timerIndex, enable);
  if (!enable) return;

  digitalWrite(m.directionPin, revsPerSec > 0 ? LOW : HIGH); // low is clockwise
  m.clockwise = revsPerSec > 0;
  revsPerSec = abs(revsPerSec);

  const float cpuFrequency = 16000000.0; // arduino constant
  const float ticksPerMicrostep = 2.0;   // we toggle high/low in our ISR
  const float microstepsPerStep = float(m.microsteps);
  const float stepsPerRev = 200.0;

  float ticksPerSec = ticksPerMicrostep * microstepsPerStep * stepsPerRev * revsPerSec;

  // top speed: 1 rev/sec
  if (ticksPerSec > 6400) {
    ticksPerSec = 6400;
  }

  float clockCyclesPerTick = cpuFrequency / ticksPerSec;

  float maxTimerCycles = m.timerIndex == 1 ? 65535 : 255;
  float idealPrescale = clockCyclesPerTick / maxTimerCycles;
  long prescale = getBestPossiblePrescale(m.timerIndex, idealPrescale);
  long waitCycles = long(clockCyclesPerTick / prescale);

  if (waitCycles >= 65536) {
    waitCycles = 65535;
  }

  m.waitCycles = waitCycles;

  if (m.prescale != prescale) {
    applyPrescale(m, prescale);
    // reset remaining cycles only if prescale changed
    // this should result in smoother speed changes
    m.waitCyclesLeft = waitCycles;
  }
}

void updateSpeed(Motor& m) {
  if (m.currentSpeed == m.targetSpeed) return;

  if (m.currentSpeed < m.targetSpeed) {
    m.currentSpeed = min(m.currentSpeed + m.acceleration, m.targetSpeed);
  } else {
    m.currentSpeed = max(m.currentSpeed - m.acceleration, m.targetSpeed);
  }

  setMotorSpeed(m, m.currentSpeed);
}

void updateSimpleMotor(SimpleMotor& m) {
  if (m.targetStepCount == 0) return;

  if (m.targetStepCount > 0) {
    digitalWrite(m.directionPin, LOW);
    m.targetStepCount -= 1;
  } else {
    digitalWrite(m.directionPin, HIGH);
    m.targetStepCount += 1;
  }

  m.stepPinState = m.stepPinState == LOW ? HIGH : LOW;
  digitalWrite(m.stepPin, m.stepPinState);
}

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(1000);

  initMotor(m1);
  initMotor(m2);
  initSimpleMotor(m3);
  initTimers();

  setMotorSpeed(m1, 0.0);
  setMotorSpeed(m2, 0.0);
}

ISR(TIMER1_OVF_vect)
{
  if (m1.waitCyclesLeft == 0) {
    // toggle step pin
    m1.stepPinState = m1.stepPinState == LOW ? HIGH : LOW;
    digitalWrite(m1.stepPin, m1.stepPinState);
    if (m1.stepPinState) m1.microstepCount += (m1.clockwise ? 1 : -1);
    // reset wait cycles counter
    m1.waitCyclesLeft = m1.waitCycles;
  }
  if (m1.waitCyclesLeft > 0) {
    long waitCyclesNow = m1.waitCyclesLeft > 65536 ? 65536 : m1.waitCyclesLeft;
    TCNT1 = 65536 - waitCyclesNow;
    m1.waitCyclesLeft -= waitCyclesNow;
  }
}

ISR(TIMER2_OVF_vect)
{
  if (m2.waitCyclesLeft == 0) {
    // toggle step pin
    m2.stepPinState = m2.stepPinState == LOW ? HIGH : LOW;
    digitalWrite(m2.stepPin, m2.stepPinState);
    if (m2.stepPinState) m2.microstepCount += (m2.clockwise ? 1 : -1);
    // reset wait cycles counter
    m2.waitCyclesLeft = m2.waitCycles;
  }
  if (m2.waitCyclesLeft > 0) {
    long waitCyclesNow = m2.waitCyclesLeft > 256 ? 256 : m2.waitCyclesLeft;
    TCNT2 = 256 - waitCyclesNow;
    m2.waitCyclesLeft -= waitCyclesNow;
  }
}

int updateSpeedsCountdown = 0;
int updateSpeedsCycle = 100;
int updateSimpleMotorCountdown = 25;
int updateSimpleMotorCycle = 50;

void loop() {
  // read commands from serial interface.
  // commands can set or get attributes.
  // axis must be given, value only on set.
  // axis may be r (RA) or d (Dec).

  // Ex: set spd axis=r value=-32543.0

  String line;
  String op;
  String attr;
  String axis;
  float value;

  if (Serial.available() > 0) {
    line = Serial.readStringUntil('\n');

    op = line.substring(0, 3);
    attr = line.substring(4, 7);
    axis = line.substring(13, 14);

    if (axis.equals("r") || axis.equals("d")) {
      // feature-rich axes. support speed, acceleration, position commands
      Motor& motor = axis.equals("r") ? m1 : m2;

      if (op.equals("set")) {
        value = line.substring(21).toFloat();
        if (attr.equals("spd")) {
          motor.targetSpeed = value;
        } else if (attr.equals("pos")) {
          motor.microstepCount = value;
        } else if (attr.equals("acl")) {
          motor.acceleration = value;
        }
      } else {
        if (attr.equals("pos")) {
          Serial.println(motor.microstepCount);
          Serial.flush();
        }
      }
    } else {
      // less feature-rich axes. support only setting target position
      SimpleMotor& motor = m3;

      if (op.equals("set")) {
        value = line.substring(21).toFloat();
        if (attr.equals("pos")) {
          motor.targetStepCount = value;
        }
      }
    }
  }

  if (updateSpeedsCountdown == 0) {
    // apply acceleration, if any
    updateSpeed(m1);
    updateSpeed(m2);
    updateSpeedsCountdown = updateSpeedsCycle;
  } else {
    updateSpeedsCountdown -= 1;
  }

  if (updateSimpleMotorCountdown == 0) {
    updateSimpleMotor(m3);
    updateSimpleMotorCountdown = updateSimpleMotorCycle;
  } else {
    updateSimpleMotorCountdown -= 1;
  }
}
