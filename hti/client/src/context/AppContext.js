import React, { Component } from 'react'
import $backend from '../backend'

export const AppContext = React.createContext()

export class AppProvider extends Component {
  constructor (props) {
    super(props)

    this.camera = null
    this.initialize()

    this.state = {
        imageUrl: null,
        imagePath: null,
        imagePosition: null,
        imageRotation: null,
        initialized: false
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

      startSequence: (pathPrefix, exposure, gain) => {
        return $backend.startSequence(this.camera, pathPrefix, exposure, gain)
      },

      stopSequence: () => {
        return $backend.stopSequence(this.camera)
      },

      queryTarget: (query) => {
        return $backend.queryTarget(query)
      },

      getSpeeds: () => {
        return $backend.getSpeeds()
      },

      setSpeeds: (raSpeed, decSpeed) => {
        return $backend.setSpeeds(raSpeed, decSpeed)
      },

      setRest: () => {
        return $backend.setRest()
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
      if (event['type'] === 'image') {
        this.setState({
          imageUrl: 'http://localhost:5000/static/' + event['image_path'],
          imagePath: event['image_path']
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
