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
  capture (exposure, gain, persist) {
    return $axios.post('/camera/capture', {
        exposure: exposure,
        gain: gain,
        persist: persist,
    })
  },

  startSequence (frameType, exposure, gain, persist) {
    return $axios.post('/camera/sequence', {
        frameType: frameType,
        exposure: exposure,
        gain: gain,
        persist: persist,
    })
  },

  stopSequence () {
    return $axios.delete('/camera/sequence')
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

  startGuiding () {
    return $axios.post('/guiding/guide')
  },

  stopGuiding () {
    return $axios.delete('/guiding/guide')
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
  }
}
