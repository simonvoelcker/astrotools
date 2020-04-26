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
  getAxisSpeed (axis) {
    return $axios.get('/axes/' + axis + '/speed')
  },

  getDevices () {
    return $axios.get('/camera/devices')
  },

  capture (deviceName, exposure, gain) {
    return $axios.get('/camera/device/' + deviceName + '/capture/' + exposure + '/' + gain)
  },

  startSequence (deviceName, pathPrefix, exposure, gain) {
    return $axios.post('/camera/device/' + deviceName + '/start_sequence', {
        pathPrefix: pathPrefix,
        exposure: exposure,
        gain: gain
    })
  },

  stopSequence (deviceName) {
    return $axios.get('/camera/device/' + deviceName + '/stop_sequence')
  }
}
