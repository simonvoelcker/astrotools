import React, { Component } from 'react'
import $backend from '../backend'

export const AppContext = React.createContext()

export class AppProvider extends Component {
  constructor (props) {
    super(props)

    this.camera = null

    this.state = {
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

      images: {
        prefix: null,     // common prefix to all image paths. relative to static
        paths: null
      },
      imageSelection: {
        directoryIndex: null,
        filenameIndex: null
      }
    }

    this.utils = {
      imagePath: () => {
        if (this.state.images.paths === null) {
          return null
        }
        let directory = this.state.images.paths[this.state.imageSelection.directoryIndex]
        let filename = directory.children[this.state.imageSelection.filenameIndex]
        return this.state.images.prefix + '/' + directory.name + '/' + filename
      },

      imageUrl: () => {
        let imagePath = this.utils.imagePath()
        if (imagePath === null) {
          return null
        }
        return 'http://localhost:5000/static/' + this.utils.imagePath()
      },

      directoryNames: () => {
        if (this.state.images.paths === null) {
          return []
        }
        return this.state.images.paths.map(directory => directory.name)
      },

      fileNames: () => {
        if (this.state.images.paths === null) {
          return []
        }
        return this.state.images.paths[this.state.imageSelection.directoryIndex].children
      },

      numFiles: () => {
        return this.utils.fileNames().length
      }
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

      listDirectory: (path, recursive) => {
        return $backend.listDirectory(path, recursive)
      },

      selectDirectory: (directory) => {
        this.setState({
          imageSelection: {
            directoryIndex: this.utils.directoryNames().indexOf(directory),
            filenameIndex: 0
          }
        })
      },

      selectPreviousImage: () => {
        let numFiles = this.utils.fileNames().length
        this.setState({
          imageSelection: {
            directoryIndex: this.state.imageSelection.directoryIndex,
            filenameIndex: (this.state.imageSelection.filenameIndex + numFiles - 1) % numFiles
          }
        })
      },

      selectNextImage: () => {
        let numFiles = this.utils.fileNames().length
        this.setState({
          imageSelection: {
            directoryIndex: this.state.imageSelection.directoryIndex,
            filenameIndex: (this.state.imageSelection.filenameIndex + 1) % numFiles
          }
        })
      }
    }

    this.initialize()
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

    this.mutations.listDirectory('.', false).then(response => {
      if (response.data.length > 0) {
        let latestPrefix = response.data[response.data.length-1]
        this.mutations.listDirectory(latestPrefix, true).then(response => {
          let paths = response.data
          this.setState({
            images: {
              prefix: latestPrefix,
              paths: paths
            },
            imageSelection: {
              directoryIndex: 0,
              filenameIndex: 0
            }
          })
        })
      }
    })
  }

  render () {
    return (
      <AppContext.Provider value={{ store: this.state, mutations: this.mutations, utils: this.utils }}>
        {this.props.children}
      </AppContext.Provider>
    )
  }
}

export const AppConsumer = AppContext.Consumer
