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
  capture (deviceName, exposure, gain, persist) {
    return $axios.post('/camera/' + deviceName + '/capture', {
        exposure: exposure,
        gain: gain,
        persist: persist,
    })
  },

  startSequence (deviceName, frameType, exposure, gain, persist) {
    return $axios.post('/camera/' + deviceName + '/start_sequence', {
        frameType: frameType,
        exposure: exposure,
        gain: gain,
        persist: persist,
    })
  },

  stopSequence (deviceName) {
    return $axios.get('/camera/' + deviceName + '/stop_sequence')
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

  startTracking (mode) {
    return $axios.post('/tracking/start', {
      mode: mode,
    })
  },

  stopTracking () {
    return $axios.post('/tracking/stop')
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
