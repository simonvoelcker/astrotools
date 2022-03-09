import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

export default class CaptureControl extends Component {

  constructor (props) {
    super(props)
    this.state = {
      exposureChange: 0,
    }
  }

  updateCameraSettings () {
    const cam = this.context.store.cameras[this.props.camera]
    $backend.updateCameraSettings(
      this.props.camera, cam.exposure, cam.gain, cam.region, cam.persist,
    )
  }

  onChangeExposure (event) {
    this.setState({exposureChange: event.target.value})
  }

  onEndChangeExposure (event) {
    this.context.store.cameras[this.props.camera].exposure = this.computeExposure();
    this.setState({exposureChange: 0})
    this.updateCameraSettings()
  }

  computeExposure () {
    const cam = this.context.store.cameras[this.props.camera]
    let exposure = cam.exposure * Math.pow(10.0, this.state.exposureChange)

    exposure = Math.min(exposure, 30)
    exposure = Math.max(exposure, 0.001)
    return this.roundToTwoDigits(exposure)
  }

  roundToTwoDigits (value) {
    // round such that only the leading two digits are nonzero
    let numDigits = Math.ceil(Math.log(value) / Math.log(10))
    let divisor = Math.pow(10, numDigits - 2)
    let rounded = divisor * Math.round(value / divisor)
    // JS-related fuckups lead to results like 1.000000000001, so:
    return Math.round(rounded * 1000) / 1000
  }

  onChangeGain (event) {
    // for better control over small values, the slider acting on this value controls the sqrt
    let value = event.target.value * event.target.value
    value = this.roundToTwoDigits(value)

    this.context.store.cameras[this.props.camera].gain = Math.round(value)
    this.updateCameraSettings()
  }

  onChangePersist (event) {
    this.context.store.cameras[this.props.camera].persist = event.target.checked
    this.updateCameraSettings()
  }

  onSelectRegion () {
    console.log("select mode")
    this.context.store.regionSelectByDeviceName[this.props.camera] = true
  }

  onClearRegion () {
    this.context.store.cameras[this.props.camera].region = null
    this.updateCameraSettings()
  }

  capture () {
    $backend.capture(this.props.camera)
  }

  startSequence () {
    $backend.startSequence(this.props.camera)
  }

  stopSequence () {
    $backend.stopSequence(this.props.camera)
  }

  render () {
    const store = this.context.store
    const cam = this.props.camera !== null ? store.cameras[this.props.camera] : null
    const panelStateClass = (cam !== null ? 'panel-green' : 'panel-red')

    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel capture-control-panel ' + panelStateClass}>

            <div className='settings-row'>
              <Label className='spaced-text'>Camera</Label>
              <Label className='spaced-text'>{this.props.camera || 'None'}</Label>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Exposure</Label>
              <input type="range" min="-1" max="1" step="0.01" className="slider" id="exposure-input"
                  value={this.state.exposureChange}
                  onChange={(event) => this.onChangeExposure(event)}
                  onMouseUp={(event) => this.onEndChangeExposure(event)} />
              <span>{cam !== null ? this.computeExposure() : 1} seconds</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Gain</Label>
              <input type="range" min="1" max="141" step="0.1" className="slider" id="gain-input"
                  disabled={cam === null}
                  value={cam !== null ? Math.sqrt(cam.gain) : 1}
                  onChange={(event) => this.onChangeGain(event)} />
              <span>{cam !== null ? cam.gain : 1}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Single capture</Label>
              <button className="btn" id="capture"
                      disabled={cam === null || cam.capturing || cam.runningSequence}
                      onClick={this.capture.bind(this)}>Capture</button>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Sequence</Label>
              { cam !== null && cam.runningSequence ?
                <button className="btn" id="stop-sequence"
                        disabled={cam === null || cam.sequenceStopRequested}
                        onClick={this.stopSequence.bind(this)}>Stop</button>
              :
                <button className="btn" id="start-sequence"
                        disabled={cam === null || cam.capturing}
                        onClick={this.startSequence.bind(this)}>Start</button>
              }
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Region</Label>
              { cam !== null && cam.region !== null ?
                <button className="btn" id="clear-region"
                        disabled={cam === null}
                        onClick={this.onClearRegion.bind(this)}>Clear</button>
              :
                <button className="btn" id="select-region"
                        disabled={cam === null || store.regionSelectByDeviceName[this.props.camera]}
                        onClick={this.onSelectRegion.bind(this)}>Select</button>
              }
              <span>{cam !== null && cam.region ? "set" : ""}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Persist</Label>
              <input type="checkbox"
                     className="checkbox-input"
                     value={cam !== null ? cam.persist : false}
                     onChange={(event) => this.onChangePersist(event)}/>{' '}
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CaptureControl.contextType = AppContext
