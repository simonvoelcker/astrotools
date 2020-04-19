import config from '../config'
import { OOF_TXT, INDUCTIVE_SENSOR_RANGE } from './Constants'

let appState = {
  // HMI state
  selectedScene: 'SceneInfos',
  doorStatus: {
    doorLocked: false,
    leftOpen: true,
    frontOpen: true,
    rightOPen: true,
    doorOpen: true
  },
  oofStatus: {
    t0Spool: false,
    t0Main: false,
    t1Spool: false,
    t1Main: false
  },
  genericModalInfo: {
    title: '',
    message: '',
    details: '',
    remedy: ''
  },
  currentModal: null,
  inductiveSensorStatus: {
    bedLeveling: INDUCTIVE_SENSOR_RANGE,
    nozzleCalib: INDUCTIVE_SENSOR_RANGE
  },
  machineHomed: null,
  mode: 'live', // default is live. other modes demo, dev
  versionInfo: null,
  machineInfo: null,
  networkInfo: null,
  pendingRequest: null,
  // print state
  runningCommand: null,
  isPaused: false,
  isHeatingUp: false,
  printingNow: false,
  elapsedPrintTime: null,
  latestElapsedPrintTime: null,
  totalPrintProgress: 0.0,
  printProgress: 0.0,
  printerStatus: [],
  InitialDataLoaded: false,
  zPos: undefined,
  changingExtrusionRate: { t0: null, t1: null },
  extrusionRates: { t0: null, t1: null },
  offsetX: null,
  offsetY: null,
  // queue/reports/meta state
  diskInfo: null,
  uploadPercentage: -1,
  uploadFileName: '',
  jobQueue: [],
  jobReports: [],
  machineInfoList: [],
  selectedMachineStatus: null,
  logMessages: [],
  newEventReceived: false,
  extruderSettingsArray: undefined,
  machineSettings: null,
  isMinimumRequiredBlade: '',
  // misc states
  socket: undefined,
  fileServerPath: config.API_URL + 'getfile/',
  stlFileName: undefined,
  OPCConnectionChecker: undefined,
  bedMapPoints: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  bedMapDelta: undefined,
  missingCommands: [],
  customCommands: undefined,
  hmiCommands: {
    bedLevelling: undefined,
    homeAxes: undefined,
    parkingPosition: undefined,
    prmExt1: undefined,
    prmExt2: undefined,
    loadFilamentExt1: undefined,
    loadFilamentExt2: undefined,
    unloadFilamentExt1: undefined,
    unloadFilamentExt2: undefined,
    zCalibExt1: undefined,
    zCalibExt2: undefined
  },
  temperatures: {
    arBed: undefined,
    arBuildChamber: undefined,
    arExtruderAvg: undefined,
    arFilamentChamber: undefined,
    bTempOkExt1: undefined,
    bTempOkExt2: undefined,
    arExtruder1: undefined,
    arExtruder2: undefined,
    rBed: undefined
  },
  arLocalMachineStates: [
    'NC program is running',
    'Heating up in progress',
    'Cooling down in progress',
    'Manual operation mode',
    'Waiting for User Action',
    'Job finished',
    'Heating up finished',
    'Cooling down finished',
    OOF_TXT.T0,
    'At least one door is open',
    'E-Stop has been triggered',
    'Channel Error',
    'Exceeding temperature limits',
    'Job is running',
    'Printer is Idle',
    'Temperature Module Error',
    'Heating Control Error',
    'Temperature System Data Error',
    'Axis in Error State',
    'Safety Error',
    'Doors are not locked',
    OOF_TXT.T1
  ]
}

export default appState
