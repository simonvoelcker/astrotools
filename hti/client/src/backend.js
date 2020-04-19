import axios from 'axios'
import config from './config'

const $axios = axios.create({
  baseURL: config.API_URL,
  timeout: 50000,
  headers: { 'Content-Type': 'application/json' }
})

// Request Interceptor
$axios.interceptors.request.use(function (config) {
  config.headers.Authorization = 'Fake Token'
  return config
})

export default {
  checkConnectedToPrinter () {
    return $axios.get('control/is-opc-connected')
  },

  startUpdate (updateFile) {
    const updateHMIResource = 'control/updatehmi/' + updateFile
    return $axios.get(updateHMIResource)
  },

  startJob (jobId) {
    const startJobResource = 'control/startjob/' + jobId
    return $axios.get(startJobResource)
  },

  getHmiMetaInfo () {
    return $axios.get('info/meta-info')
  },

  isPrinterHomed () {
    return $axios.get('control/homeprinter')
  },

  getDiskInfo () {
    return $axios.get('info/disk-info')
  },

  homePrinter () {
    return $axios.post('control/homeprinter')
  },

  resetPrinter () {
    return $axios.get('control/resetprinter')
  },

  pauseJob () {
    return $axios.get('control/pausejob')
  },

  resumeJob () {
    return $axios.get('control/resumejob')
  },

  stopJob () {
    return $axios.get('control/stopjob')
  },

  uploadFile (formData, configData) {
    return $axios.post('jobs/single-file', formData, configData)
  },

  loadControlJob (filename, jobName) {
    return $axios.post('jobs/control-job', { filename: filename, job_name: jobName })
  },

  removeJob (jobId) {
    const removeJobResource = 'jobs/delete-job/' + jobId
    return $axios.delete(removeJobResource)
  },

  setDoorLock (lockDoor) {
    const doorLockResource = 'control/door-lock/' + lockDoor
    return $axios.post(doorLockResource)
  },

  setExtrusionRate (tool, extrusionRate) {
    return $axios.post('control/extrusion-rate/' + tool + '/' + extrusionRate)
  },

  getJobFileList () {
    return $axios.get('jobs/all-file/json')
  },

  setJobPosition (jobId, position) {
    let setJobPositionResource = 'jobs/reorder-job/' + jobId + '/' + position
    return $axios.post(setJobPositionResource)
  },

  downloadJobReportFile (filename) {
    const jobReportFileResource = 'jobs/report-file/' + filename
    return $axios.get(jobReportFileResource, { responseType: 'blob' })
  },

  getJobReports () {
    return $axios.get('jobs/all-report-file')
  },

  getMachineInfoList () {
    return $axios.get('info/machine-info')
  },

  getMachineInfo (machineInfoId) {
    let getMachineInfoResource = 'info/machine-info/' + machineInfoId
    return $axios.get(getMachineInfoResource)
  },

  getInstalledCommands () {
    return $axios.get('control/command')
  },

  getDCorrections () {
    return $axios.get('control/d-corrections')
  },

  setDCorrections (newOffsets) {
    return $axios.post('control/d-corrections', newOffsets)
  },

  runCommand (command) {
    return $axios.post('control/command', command)
  },

  setTemperature (tool, temperature) {
    return $axios.post('control/temperature', { tool: tool, temperature: temperature })
  },

  setExtruder (serial_number, extruder_type, desc) {
    return $axios.post('info/extruder-info', { serial_number: serial_number, extruder_type: extruder_type, desc: desc })
  },

  updateExtruder (serial_number, extruder_type, desc) {
    return $axios.put('info/extruder-info', { serial_number: serial_number, extruder_type: extruder_type, desc: desc })
  },

  getBedMap () {
    return $axios.get('control/bed-map')
  },

  moveAxis (direction, distance) {
    return $axios.post('control/move-axis', { direction: direction, distance: distance })
  },

  logMessage (message) {
    return $axios.post('info/log-message', message)
  },

  getLog () {
    return $axios.get('info/log-message')
  },

  exitHmi () {
    return $axios.post('control/exit')
  }
}
