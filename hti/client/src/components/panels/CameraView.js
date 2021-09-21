import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import StandardButton from '../panels/StandardButton'
import { Input } from 'reactstrap'
import $backend from '../../backend'

export default class CameraView extends Component {

  constructor (props) {
    super(props)
    this.state = {
      brightness: 1.0,
      contrast: 1.0,
      saturation: 1.0,
    }
  }

  onChangeBrightness (event) {
    this.setState({brightness: event.target.value})
  }

  onChangeContrast (event) {
    this.setState({contrast: event.target.value})
  }

  onChangeSaturation (event) {
    this.setState({saturation: event.target.value})
  }

  resetSettings () {
    this.setState({
      brightness: 1.0,
      contrast: 1.0,
      saturation: 1.0,
    })
  }

  onImgMouseDown (event) {
    let store = this.context.store

    if (store.regionSelectByDeviceName[this.props.camera]) {
      let imageElement = event.target
      let normalizedX = (event.pageX - imageElement.x) / imageElement.width
      let normalizedY = (event.pageY - imageElement.y) / imageElement.height

      let frameX = Math.round(normalizedX * store.cameras[this.props.camera]["frameWidth"])
      let frameY = Math.round(normalizedY * store.cameras[this.props.camera]["frameHeight"])

      const regionRadius = 100

      store.cameras[this.props.camera].region = [
          frameX - regionRadius,
          frameY - regionRadius,
          2 * regionRadius,
          2 * regionRadius,
      ]
      // clear selection mode
      store.regionSelectByDeviceName[this.props.camera] = false

      $backend.updateCameraSettings(
        this.props.camera,
        store.cameras[this.props.camera].exposure,
        store.cameras[this.props.camera].gain,
        store.cameras[this.props.camera].region,
        store.cameras[this.props.camera].persist,
      )
    }
  }

  render () {
    const store = this.context.store

    let imageSource = ""
    if (this.props.camera !== null && store.framePathByDeviceName[this.props.camera] !== null) {
        let path = encodeURIComponent(store.framePathByDeviceName[this.props.camera])
        imageSource = "http://localhost:5000/api/camera/frames?framePath=" + path
    }

    let width = 0
    let height = 0
    if (this.props.camera !== null) {
        width = store.cameras[this.props.camera]["frameWidth"]
        height = store.cameras[this.props.camera]["frameHeight"]
    }

    const filter = "brightness(" + this.state.brightness + ") "
                 + "saturate(" + this.state.saturation + ") "
                 + "contrast(" + this.state.contrast + ") "

    return (
      <AppConsumer>
        {({ store }) => (
          <div className='panel camera-view-panel'>
            <img id="camera-image"
              alt=''
              style={{"filter": filter}}
              src={imageSource}
              onMouseDown={this.onImgMouseDown.bind(this)} />

            <div className="image-view-options">
              <span className="spaced-text">Brightness:</span>
              <Input type="range" min="0.5" max="3" step="0.1" className="slider"
                value={this.state.brightness}
                onChange={this.onChangeBrightness.bind(this)} />
              <span className="spaced-text">Contrast:</span>
              <Input type="range" min="0.5" max="3" step="0.1" className="slider"
                value={this.state.contrast}
                onChange={this.onChangeContrast.bind(this)} />
              <span className="spaced-text">Saturation:</span>
              <Input type="range" min="0" max="2" step="0.1" className="slider"
                value={this.state.saturation}
                onChange={this.onChangeSaturation.bind(this)} />
              <StandardButton onClick={() => {this.resetSettings()}}>Reset</StandardButton>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
