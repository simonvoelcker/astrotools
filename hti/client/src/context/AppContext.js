import React, { Component } from 'react'

export const AppContext = React.createContext()

export class AppProvider extends Component {
  constructor (props) {
    super(props)

    this.state = {
      // via app_state event
      cameras: {},

      axesConnected: null,
      axesSim: null,
      steering: null,
      guiding: null,
      calibrating: null,
      target: null,
      axisSpeeds: null,
      lastKnownPosition: {
        timestamp: null,
        position: null,
      },

      annotations: null,

      // via image event
      framePathByDeviceName: {},

      // via log event
      logEntries: [
        {timestamp: Date.now(), text: 'Frontend started'},
      ],

      pecState: {
        recording: null,
        ready: null,
        correcting: null,
        factor: null,
      },

      capturingCamera: null,
      guidingCamera: null,
    }

    this.initialize()
  }

  initialize () {

    const maxLogLength = 30

    let eventListener = new EventSource('http://localhost:5000/api/info/events')
    eventListener.onmessage = (event) => {
      event = JSON.parse(event.data)
      if (event['type'] === 'app_state') {
        this.setState(event['appState'])

        // todo should only do this once and pick the
        // capturing camera by resolution
        let cameras = event['appState']['cameras']
        if (cameras !== null) {
          let cameraNames = Object.keys(cameras)
          if (cameraNames.length > 0) {
            this.setState({capturingCamera: cameraNames[0]})
          }
          if (cameraNames.length > 1) {
            this.setState({guidingCamera: cameraNames[1]})
          }
        }

      } else if (event['type'] === 'image') {
        // TODO use setState... it is messing with me rn
        this.state.framePathByDeviceName[event['deviceName']] = event['imagePath']
      } else if (event['type'] === 'log') {
        this.setState({
          logEntries: this.state.logEntries.concat({
            timestamp: Date.now(),
            text: event['text'],
          }).slice(-maxLogLength)
        })
      }
    }
  }

  render () {
    return (
      <AppContext.Provider value={{ store: this.state }}>
        {this.props.children}
      </AppContext.Provider>
    )
  }
}

export const AppConsumer = AppContext.Consumer
