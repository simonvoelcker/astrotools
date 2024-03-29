import axios from 'axios'

const $axios = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '/api/' : 'http://localhost:5000/api/',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

// Request Interceptor
$axios.interceptors.request.use((config) => {
  config.headers.Authorization = 'Fake Token'
  return config
})

export default {

  updateCameraSettings(device, exposure, gain, region, persist) {
    return $axios.put('/camera/settings', {
        device: device,
        exposure: exposure,
        gain: gain,
        region: region,
        persist: persist,
    })
  },

  capture (device) {
    return $axios.post('/camera/capture', {device: device})
  },

  startSequence (device) {
    return $axios.post('/camera/sequence', {device: device})
  },

  stopSequence (device) {
    return $axios.delete('/camera/sequence?device=' + device)
  },

  listSequences () {
    return $axios.get('/analyzer/sequences/')
  },

  analyzeSequence (sequenceId) {
    return $axios.post('/analyzer/sequences/' + sequenceId + '/analyze')
  },

  deleteSequence (sequenceId) {
    return $axios.delete('/analyzer/sequences/' + sequenceId)
  },

  listFrames (sequenceId) {
    return $axios.get('/analyzer/sequences/' + sequenceId + '/frames/')
  },

  getFramePath (frameId) {
    return $axios.get('/analyzer/frames/' + frameId + '/path')
  },

  analyzeFrame (frameId) {
    return $axios.post('/analyzer/frames/' + frameId + '/analyze')
  },

  deleteFrame (frameId) {
    return $axios.delete('/analyzer/frames/' + frameId)
  },

  stackSequence (sequenceId) {
    return $axios.post('/stacking/stack', {
      lightsSequenceId: sequenceId,
    })
  },

  getStackedImagePreview (stackedImageHash) {
    return $axios.get('/stacking/preview/' + stackedImageHash)
  },

  queryTarget (query) {
    return $axios.get('/info/target/' + query)
  },

  setSpeeds (raSpeed, decSpeed) {
    return $axios.post('/axes/speeds', {
        ra: raSpeed,
        dec: decSpeed,
    })
  },

  setRest () {
    return $axios.post('/axes/rest')
  },

  calibrateFrame (framePath, timeout) {
    return $axios.post('/info/images/calibrate', {
      framePath: framePath,
      timeout: timeout,
    })
  },

  stopCalibration () {
    return $axios.post('/info/images/calibrate/stop')
  },

  startGuiding (device, settings) {
    return $axios.post('/guiding/guide', {device: device, settings: settings})
  },

  stopGuiding (device) {
    return $axios.delete('/guiding/guide?device=' + device)
  },

  startPECRecording () {
    return $axios.post('/pec/record')
  },

  stopPECRecording () {
    return $axios.delete('/pec/record')
  },

  startPECReplay () {
    return $axios.post('/pec/replay')
  },

  stopPECReplay () {
    return $axios.delete('/pec/replay')
  },

  setPECFactor (factor) {
    return $axios.post('/pec/set-factor', {
      factor: factor,
    })
  },

  goToTarget () {
    return $axios.post('/axes/gototarget')
  },

  listDirectory (path, recursive) {
    return $axios.post('/info/directory', {
      path: path,
      recursive: recursive,
    })
  },

  getStars (count, minRa, maxRa, minDec, maxDec) {
    return $axios.get('/info/stars', { params: {
        count: count,
        minRa: minRa,
        maxRa: maxRa,
        minDec: minDec,
        maxDec: maxDec,
    }})
  },

  moveFocus (steps) {
    return $axios.post('/axes/focus', {
      steps: steps,
    })
  },

  autoFocus () {
    return $axios.post('/axes/auto-focus')
  }
}
