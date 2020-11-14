import React, { Component } from 'react'
import $backend from '../backend'

export const AppContext = React.createContext()

export class AppProvider extends Component {
  constructor (props) {
    super(props)

    this.state = {
      initialized: false,  // todo need a state to mean "backend state received"

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

      // image browsing stuff - out of order atm
      images: {
        prefix: null,     // common prefix to all image paths. relative to static
        paths: null       // todo augment this with image calibration data. also move it to a class: ImageStore, with some nice util stuff
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
      },

      calibrateImage (context) {
        let imagePath = context.store.imagePath
        return $backend.calibrateImage(imagePath)
      }
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
