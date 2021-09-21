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
      axisSpeeds: null,

      // goto
      steering: null,
      calibrating: null,
      target: null,
      lastKnownPosition: {
        timestamp: null,
        position: null,
      },

      guiding: null,

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

      // add camera config event with cam info
      capturingCamera: null,
      guidingCamera: null,

      // bool by device name whether or not region selection mode is on
      regionSelectByDeviceName: {},
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

        // TODO this whole thing should be a different event
        // configChangeEvent or so
        let cameras = event['appState']['cameras']
        if (cameras !== null) {
          let cameraNames = Object.keys(cameras)
          if (cameraNames.length == 1) {
            this.setState({
              guidingCamera: null,
              capturingCamera: cameraNames[0],
            })
          }
          if (cameraNames.length == 2) {
            // sort ascending by resolution
            cameraNames = cameraNames.sort((name1, name2) => {
                return cameras[name1]["frameWidth"] * cameras[name1]["frameHeight"]
                     - cameras[name2]["frameWidth"] * cameras[name2]["frameHeight"]
            })
            this.setState({
              guidingCamera: cameraNames[0],
              capturingCamera: cameraNames[1],
            })
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
