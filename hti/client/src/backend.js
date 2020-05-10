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
  getDevices () {
    return $axios.get('/indi/devices')
  },

  capture (deviceName, exposure, gain) {
    return $axios.post('/camera/' + deviceName + '/capture', {
        exposure: exposure,
        gain: gain
    })
  },

  startSequence (deviceName, pathPrefix, exposure, gain) {
    return $axios.post('/camera/' + deviceName + '/start_sequence', {
        pathPrefix: pathPrefix,
        exposure: exposure,
        gain: gain
    })
  },

  stopSequence (deviceName) {
    return $axios.get('/camera/' + deviceName + '/stop_sequence')
  },

  queryTarget (query) {
    return $axios.get('/info/target/' + query)
  },

  getSpeeds () {
    return $axios.get('/axes/speeds')
  },

  setSpeeds (raSpeed, decSpeed) {
    return $axios.post('/axes/speeds', {
        ra: raSpeed,
        dec: decSpeed
    })
  },

  setRest () {
    return $axios.post('/axes/rest')
  },

  calibrateImage (imagePath) {
    return $axios.post('/info/images/calibrate', {
      imagePath: imagePath,
      timeout: 60
    })
  },

  startTracking (mode) {
    return $axios.post('/tracking/start', {
      mode: mode
    })
  },

  stopTracking () {
    return $axios.post('/tracking/stop')
  }
}
