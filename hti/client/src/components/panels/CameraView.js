import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input } from 'reactstrap'

export default class CameraView extends Component {

  constructor (props) {
    super(props)
    this.state = {
      brightness: 1.0,
      contrast: 1.0,
      saturation: 1.0,

      showRect: false,
      mouseDownXY: {x: 0, y: 0},
      mouseUpXY: {x: 0, y: 0},
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
    let imageElement = event.target
    let normalizedX = (event.pageX - imageElement.x) / imageElement.width
    let normalizedY = (event.pageY - imageElement.y) / imageElement.height
    this.setState({
      mouseDownXY: {x: normalizedX, y: normalizedY},
      showRect: false,
    })

    console.log("down " + normalizedX + " " + normalizedY)
  }

  onImgMouseUp (event) {
    let imageElement = event.target
    let normalizedX = (event.pageX - imageElement.x) / imageElement.width
    let normalizedY = (event.pageY - imageElement.y) / imageElement.height
    this.setState({
      mouseUpXY: {x: normalizedX, y: normalizedY},
      showRect: true,
    })

    console.log("up " + normalizedX + " " + normalizedY)
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
              onMouseDown={this.onImgMouseDown.bind(this)}
              onMouseUp={this.onImgMouseUp.bind(this)} />

            {this.state.showRect &&
              <svg viewBox="0 0 1920 1080">
                <rect key="hello"
                  x={this.state.mouseDownXY.x * 1920}
                  y={this.state.mouseDownXY.y * 1080}
                  width={100}
                  height={100}
                  style={{ "fillOpacity": "0", "strokeWidth": "2", "stroke": "rgb(0,255,0)" }} />
              </svg>
            }

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
