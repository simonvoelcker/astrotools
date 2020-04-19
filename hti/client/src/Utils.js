export {
  formatMemory,
  formatDuration,
  formatTemperature,
  formatTargetTemperature,
  getTotalProgressFromPrinterState,
  extractMachineStatus,
  parseElapsedTime,
  createPrintEndDayString,
  createPrintEndDateString,
  formatPrintTimes,
  getGcodeFile,
  jobIsStarted,
  getJobTimeEstimate,
  formatSlicerVersion
}

function formatMemory (bytes) {
  // format given number of bytes as human-readable string (eg: 1.2KB)
  let mantissa = Number(bytes)
  let exponent = 0
  while (mantissa >= 1024) {
    mantissa /= 1024
    exponent += 1
  }
  const unit = ['B', 'KB', 'MB', 'GB', 'TB'][exponent]
  return mantissa.toFixed(1) + ' ' + unit
}

function formatTemperature (temperatureOrArray, type) {
  // Sensors are redundant, but prone to errors, which show as zero values.
  // If such a sensor reading array is given, we pick the mean of all non-zero values.
  // In the case for the filament chamber, the array is even nested, so we must flatten it.

  let temperature = temperatureOrArray
  if (Array.isArray(temperatureOrArray)) {
    // Array.flat exists but has bad browser support, and fails in Cypress.
    let flatten = (arr) => [].concat(...arr)
    let temperatures = flatten(temperatureOrArray).filter(x => (type === 'chamber' ? (x > 0 && x < 100) : x))
    if (temperatures.length !== 0) {
      let sum = temperatures.reduce((a, b) => a + b)
      temperature = sum / temperatures.length
    } else {
      temperature = 0.0
    }
  }
  if (temperature === 0.0) {
    return 'N/A'
  } else if (type === 'chamber' && (temperature < 0 || temperature >= 100)) {
    return 'ERR'
  }
  return parseFloat(Math.round(temperature * 10) / 10).toFixed(1)
}

function formatTargetTemperature (targetTemperature) {
  return parseInt(targetTemperature, 10)
}

function getTotalProgressFromPrinterState (printerStatus, printingProgress) {
  let newTotalPrintProgress = 0

  if (printerStatus.includes('Heating up in progress')) newTotalPrintProgress = 0.12

  if (printerStatus.includes('Job is running')) {
    newTotalPrintProgress = (printingProgress * 0.74) + 0.12
  }

  if (printerStatus.includes('Cooling down in progress')) newTotalPrintProgress = 1

  return newTotalPrintProgress
}

function extractMachineStatus (newPrinterUpdate, localMachineStatesTexts) {
  const statusArray = newPrinterUpdate['.stLocalMachineStates.arLocalMachineStates']
  let machineStatus = []

  if (statusArray === undefined) {
    return 'Problem reading machine status'
  }

  let i
  while ((i = statusArray.indexOf(true, i + 1)) !== -1) {
    machineStatus.push(localMachineStatesTexts[i])
  }

  if (machineStatus.length === 0) {
    machineStatus.push(localMachineStatesTexts[14])
  }

  return machineStatus
  // Find more documentation here: https://wiki.bigrep.com/display/PRO/Traffic+Lights

  // 0 NC Running  Any NC program is running, axes might move
  // 1 Heating Up  Temperature controllers are switched on but set points are not yet reached
  // 2 Cooling Down    Temperature controllers are switched off but actual temperature readings are not yet below threshold temperature
  // 3 Executing Command   NC is in Manual or in MDI mode, axes might move
  // 4 Standby Waiting for User Action, M0 Command issued
  // 5 Print Job Finished  A PrintJob has finished , M30 Command issued at the end of G-Code
  // 6 Heating Finished    Temperature controllers are switched on and set points are reached
  // 7 Cool Down Finished  Temperature controllers are switched off and actual temperature readings are below threshold temperature
  // 8 Out of filament on T0    Printer runs out of filament while print job is active
  // 9 Door Open   One of the doors are open while NC is in running state
  // 10 E-Stop  E-Stop has been triggered
  // 11 Channel Error
  // 12 Exceeding temperature limits
  // 13 Print Job Running   Printer is printing
  // 14 Printer is in Idle state, e.g cool down is finished, no job is due, no error, NC not running
  // 15 Temperature Module Error
  // 16 Heating Control Error
  // 17 Temperature System Data Error
  // 18 Axis in Error State
  // 19 Safety Error
  // 20 Doors are not locked
  // 21 Out of filament on T1
}

function parseElapsedTime (elapsedTimeStr) {
  // parse value of .stMachineStatus.strElapsedTime node, which is in a cryptic format:
  // format is 1d1h2m3s4ms, where zero-values components are omitted (e.g. 1h1ms is valid)
  const regex = /((?<days>\d+)d)?((?<hours>\d+)h)?((?<minutes>\d+)m(?!s))?((?<seconds>\d+)s)?((?<milliseconds>\d+)ms)?/
  const regexMatch = regex.exec(elapsedTimeStr)
  if (regexMatch === null) {
    // fallback to what is planned to be used in the future: a simple number of seconds.
    return parseInt(elapsedTimeStr)
  }
  const days = parseInt(regexMatch.groups.days || 0)
  const hours = parseInt(regexMatch.groups.hours || 0)
  const minutes = parseInt(regexMatch.groups.minutes || 0)
  const seconds = parseInt(regexMatch.groups.seconds || 0)
  return days * 86400 + hours * 3600 + minutes * 60 + seconds
}

function createPrintEndDayString (sec) {
  if (sec == null) {
    return 'Unknown'
  }
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const date = new Date()
  date.setSeconds(date.getSeconds() + sec)
  return days[date.getDay()] + ','
}

function createPrintEndDateString (sec) {
  if (sec == null) {
    return ''
  }
  const months = [' Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const date = new Date()
  date.setSeconds(date.getSeconds() + sec)
  const hours = date.getHours() > 12 ? date.getHours() - 12 : date.getHours()
  const ampm = date.getHours() > 12 ? 'PM' : 'AM'
  return months[date.getMonth()] + ' ' + date.getDate() + ',\n' +
          hours + ':' + String(date.getMinutes()).padStart(2, '0') + ' ' + ampm
}

function formatPrintTimes (sec) {
  if (sec === null) {
    return { hours: '00', minutes: '00', seconds: '00' }
  }
  const hours = Math.floor(sec / (60 * 60))
  const minutes = Math.floor((sec % (60 * 60)) / 60)
  const seconds = (sec % 60)

  return {
    hours: String(hours).padStart(2, '0'),
    minutes: String(minutes).padStart(2, '0'),
    seconds: String(seconds).padStart(2, '0')
  }
}

function formatDuration (seconds) {
  if (seconds === 'unknown') {
    return 'Unknown'
  }

  // format given number of seconds as human-readable duration (e.g. "12 minutes")
  let minutes = Math.floor(seconds / 60)
  let hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  seconds = seconds % 60
  minutes = minutes % 60
  hours = hours % 24

  let components = []
  if (days > 0) { components.push(days + ' day' + (days !== 1 ? 's' : '')) }
  if (hours > 0) { components.push(hours + ' hour' + (hours !== 1 ? 's' : '')) }
  if (minutes > 0) { components.push(minutes + ' minute' + (minutes !== 1 ? 's' : '')) }
  if (seconds > 0) { components.push(seconds + ' second' + (seconds !== 1 ? 's' : '')) }

  return components !== [] ? components.join(', ') : '0 minutes'
}

function getGcodeFile (job) {
  const gcodeFile = job.files.find(file => {
    return file.extension === '.gcode'
  })
  return gcodeFile || null
}

function jobIsStarted (job) {
  var gcodeFile = getGcodeFile(job)
  if (!gcodeFile) {
    return false
  }
  if (gcodeFile.startPrint && !gcodeFile.abortPrint && !gcodeFile.finishPrint) {
    return true
  }
  return false
}

function getGcodeFileInfo(jobInfo) {
  const firstJobFileInfo = jobInfo
  if (firstJobFileInfo === undefined) {
    return null
  }
  for (var file of firstJobFileInfo.files) {
    if (file.extension === '.gcode')
      return file
  }
  return null
}

function getJobTimeEstimate (jobInfo, printingNow) {
  let file = getGcodeFileInfo(jobInfo)
  if (file === null) return null
  if (file.time !== 'unknown') {
    return Number(file.time)
  }
  return null
}

function formatSlicerVersion (store) {
  if (store.jobQueue[0] === undefined)
    return '(no job in queue)'
  let file = getGcodeFileInfo(store.jobQueue[0])
  if (file === null) return 'Unknown'
  if (file.slicer_version !== 'unknown' && file.slicer_version !== undefined) {
    return file.slicer_version
  }
  return 'Unknown'
}
