import React, { Component } from 'react'
import * as BABYLON from 'babylonjs'
import PropTypes from 'prop-types'

// @NOTE: This one is assumed to be best practise and is documented originally here:
// https://doc.babylonjs.com/resources/babylonjs_and_reactjs

export default class Scene extends Component {
  onResizeWindow = () => {
    if (this.engine) {
      this.engine.resize()
    }
  }

  componentDidMount () {
    this.engine = new BABYLON.Engine(
      this.canvas,
      true,
      this.props.engineOptions,
      this.props.adaptToDeviceRatio
    )
    this.engine.disableManifestCheck = true
    this.engine.enableOfflineSupport = false
    this.engine.renderEvenInBackground = true

    let scene = new BABYLON.Scene(this.engine)
    this.scene = scene

    if (typeof this.props.onSceneMount === 'function') {
      this.props.onSceneMount({
        scene,
        engine: this.engine,
        canvas: this.canvas
      })
    } else {
      console.error('onSceneMount function not available')
    }

    // Resize the babylon engine when the window is resized
    window.addEventListener('resize', this.onResizeWindow)
  }

  componentWillUnmount () {
    window.removeEventListener('resize', this.onResizeWindow)
  }

  onCanvasLoaded = (c) => {
    if (c !== null) {
      this.canvas = c
    }
  }

  render () {
    return (
      <canvas
        id='renderCanvas'
        touch-action='none'
        ref={this.onCanvasLoaded}
      />
    )
  }
}

Scene.propTypes = {
  onSceneMount: PropTypes.func,
  engineOptions: PropTypes.object,
  adaptToDeviceRatio: PropTypes.bool
}
