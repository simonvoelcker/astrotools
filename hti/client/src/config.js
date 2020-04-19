// local development settings. note that localhost will NOT work in labs.
let apiUrl = 'http://localhost:5000/api/'
let webSocketUrl = 'ws://localhost:5000/'

if (process.env.NODE_ENV === 'production') {
  apiUrl = '/api/'
  webSocketUrl = '/'
}

const config = {
  API_URL: apiUrl,
  WEBSOCKET_URL: webSocketUrl
}

export default config
