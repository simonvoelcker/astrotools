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
        initialized: false
    }

    this.mutations = {
      getAxisSpeed: (axis) => {
        $backend.getAxisSpeed(axis)
          .then(response => {
            console.log('Success, ' + response)
          }).catch(error => {
            console.log('Error, ' + error)
          })
      },

      updateImage: (url) => {
        this.setState({imageUrl: url})
      },

      capture: (exposure, gain) => {
        if (this.camera !== null) {
          return $backend.capture(this.camera, exposure, gain)
        }
      },

      startSequence: (pathPrefix, exposure, gain) => {
        if (this.camera !== null) {
          return $backend.startSequence(this.camera, pathPrefix, exposure, gain)
        }
      },

      stopSequence: () => {
        if (this.camera !== null) {
          return $backend.stopSequence(this.camera)
        }
      },

      queryTarget: (query) => {
        return $backend.queryTarget(query)
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
        this.setState({imageUrl: 'http://localhost:5000/' + event['image_url']})
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
