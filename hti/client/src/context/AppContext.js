import React, { Component } from 'react'
import $backend from '../backend'

export const AppContext = React.createContext()

export class AppProvider extends Component {
  constructor (props) {
    super(props)

    this.camera = null
    this.initialize()

    this.state = {
        // todo there's a default here because the layout is not stable otherwise
        imageUrl: 'http://localhost:5000/static/2020-05-28/lights/2020-05-28T23:08:42.301155.png',
        imagePath: '2020-05-28/lights/2020-05-28T23:08:42.301155.png',
        imagePosition: null,
        imageRotation: null,
        initialized: false,  // todo need a state to mean "backend state received"
        trackingStatus: null,

        // from backend (app state events):
        runningSequence: null,
        steering: null,
        tracking: null,
        calibrating: null,
        here: null,
        target: null,  // todo this is only coordinates, no meta data
        axisSpeeds: null,
    }

    this.mutations = {

      calibrateImage: (imagePath) => {
        return $backend.calibrateImage(imagePath).then(response => {
          this.setState({
            imagePosition: {
              ra: parseFloat(response.data.center_deg.ra),
              dec: parseFloat(response.data.center_deg.dec)
            },
            imageRotation: {
              angle: parseFloat(response.data.rotation.angle),
              direction: response.data.rotation.direction
            }
          })
        }).catch(error => {
          this.setState({
            imagePosition: null,
            imageRotation: null
          })
        })
      },

      capture: (exposure, gain) => {
        return $backend.capture(this.camera, exposure, gain)
      },

      startSequence: (frameType, exposure, gain) => {
        return $backend.startSequence(this.camera, frameType, exposure, gain)
      },

      stopSequence: () => {
        return $backend.stopSequence(this.camera)
      },

      queryTarget: (query) => {
        return $backend.queryTarget(query)
      },

      setSpeeds: (raSpeed, decSpeed) => {
        return $backend.setSpeeds(raSpeed, decSpeed)
      },

      setRest: () => {
        return $backend.setRest()
      },

      startTracking: (mode) => {
        return $backend.startTracking(mode)
      },

      stopTracking: () => {
        return $backend.stopTracking()
      },

      goToTarget: () => {
        return $backend.goToTarget()
      },

      listDirectory: (path) => {
        return $backend.listDirectory(path)
      }
    }
  }

  initialize () {
    $backend.getDevices().then((response) => {
      let deviceNames = Object.keys(response.data)
      if (deviceNames.length > 0) {
        this.camera = deviceNames[0]
        this.setState({initialized: true})
      }
    })

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
      } else if (event['type'] === 'tracking_status') {
        this.setState({
          trackingStatus: {
            message: event['message'],
            unixTimestamp: event['unixTimestamp'],
            details: event['details']
          }
        })
      }
    }
  }

  render () {
    return (
      <AppContext.Provider value={{ store: this.state, mutations: this.mutations }}>
        {this.props.children}
      </AppContext.Provider>
    )
  }
}

export const AppConsumer = AppContext.Consumer
