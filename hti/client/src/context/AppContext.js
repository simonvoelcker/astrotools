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
      framePath: null,

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
        debugger;
      } else if (event['type'] === 'image') {
        this.setState({
          framePath: event['imagePath']
        })
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
