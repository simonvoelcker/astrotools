import React, { Component } from 'react'

export const AppContext = React.createContext()

export class AppProvider extends Component {
  constructor (props) {
    super(props)

    this.state = {
      // from backend (app state events):
      cameraConnected: null,
      cameraSim: null,
      axesConnected: null,
      axesSim: null,
      capturing: null,
      runningSequence: null,
      steering: null,
      tracking: null,
      trackingStatus: null,
      calibrating: null,
      target: null,  // todo this is only coordinates, no meta data
      axisSpeeds: null,

      lastKnownPosition: {
        timestamp: null,
        position: null,
      },
      lastCalibrationResult: {
        timestamp: null,
        success: null,
      },

      imageUrl: null,
      imagePath: null,

      logEntries: [
        {text: 'dummy line 1'},
        {text: 'dummy line 2'},
      ],
    }

    this.initialize()
  }

  initialize () {
    let eventListener = new EventSource('http://localhost:5000/api/info/events')
    eventListener.onmessage = (event) => {
      event = JSON.parse(event.data)
      if (event['type'] === 'app_state') {
        console.log(event['appState'])
        this.setState(event['appState'])
      } else if (event['type'] === 'image') {
        this.setState({
          imageUrl: 'http://localhost:5000/static/' + event['imagePath'],
          imagePath: event['imagePath']
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
