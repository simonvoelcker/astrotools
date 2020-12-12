import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { Input } from 'reactstrap'

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

  render () {
    const store = this.context.store

    // fallback if not frame is loaded yet
    let imageSource = "https://via.placeholder.com/960x540.png"
    if (store.framePath !== null) {
        imageSource = "http://localhost:5000/api/camera/frames?framePath=" + encodeURIComponent(store.framePath)
    }

    const filter = "brightness(" + this.state.brightness + ") "
                 + "saturate(" + this.state.saturation + ") "
                 + "contrast(" + this.state.contrast + ") "

    return (
      <AppConsumer>
        {({ store }) => (
          <div className='panel camera-view-panel'>
            <img id="camera-image" alt='' style={{"filter": filter}} src={imageSource} />
            {store.annotations !== null &&
              <svg viewBox="0 0 1920 1080">
                {store.annotations.map(a => (
                  <rect x={a.x} y={a.y} width={a.width} height={a.height}
                   style={{ "fill-opacity": "0", "stroke-width": "2", "stroke": "rgb(0,255,0)" }} />
                ))}
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
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
