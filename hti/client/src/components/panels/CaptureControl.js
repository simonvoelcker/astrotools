import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

export default class CaptureControl extends Component {

  updateCameraSettings () {
    $backend.updateCameraSettings(
      this.props.camera,
      this.context.store.cameras[this.props.camera].exposure,
      this.context.store.cameras[this.props.camera].gain,
      this.context.store.cameras[this.props.camera].region,
      this.context.store.cameras[this.props.camera].persist,
    )
  }

  onChangeExposure (event) {
    this.context.store.cameras[this.props.camera].exposure = event.target.value
    this.updateCameraSettings()
  }

  onChangeGain (event) {
    // for better control over small values, the slider acting on this value controls the sqrt
    let value = event.target.value * event.target.value

    // round such that only the leading two digits are nonzero
    let numDigits = Math.ceil(Math.log(value) / Math.log(10))
    let divisor = Math.pow(10, numDigits - 2)
    value = divisor * Math.round(value / divisor)

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
    const panelStateClass = (this.props.camera !== null ? 'panel-green' : 'panel-red')

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
              <input type="range" min="0.1" max="30" step="0.1" className="slider" id="exposure-input"
                  disabled={this.props.camera === null}
                  value={this.props.camera !== null ? store.cameras[this.props.camera].exposure : 1}
                  onChange={(event) => this.onChangeExposure(event)} />
              <span>{this.props.camera !== null ? store.cameras[this.props.camera].exposure : 1} seconds</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Gain</Label>
              <input type="range" min="1" max="141" step="0.1" className="slider" id="gain-input"
                  disabled={this.props.camera === null}
                  value={this.props.camera !== null ? Math.sqrt(store.cameras[this.props.camera].gain) : 1}
                  onChange={(event) => this.onChangeGain(event)} />
              <span>{this.props.camera !== null ? store.cameras[this.props.camera].gain : 1}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Single capture</Label>
              <StandardButton id="capture"
                      disabled={
                        this.props.camera === null ||
                        store.cameras[this.props.camera].capturing ||
                        store.cameras[this.props.camera].runningSequence
                      }
                      onClick={this.capture.bind(this)}>Capture</StandardButton>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Sequence</Label>
              { this.props.camera !== null && store.cameras[this.props.camera].runningSequence ?
                <StandardButton id="stop-sequence"
                        disabled={this.props.camera === null}
                        onClick={this.stopSequence.bind(this)}>Stop</StandardButton>
              :
                <StandardButton id="start-sequence"
                        disabled={this.props.camera === null || store.cameras[this.props.camera].capturing}
                        onClick={this.startSequence.bind(this)}>Start</StandardButton>
              }
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Region</Label>
              { this.props.camera !== null && store.cameras[this.props.camera].region !== null ?
                <StandardButton id="clear-region"
                        disabled={this.props.camera === null}
                        onClick={this.onClearRegion.bind(this)}>Clear</StandardButton>
              :
                <StandardButton id="select-region"
                        disabled={this.props.camera === null || store.regionSelectByDeviceName[this.props.camera]}
                        onClick={this.onSelectRegion.bind(this)}>Select</StandardButton>
              }
              <span>{this.props.camera !== null && store.cameras[this.props.camera].region ? "set" : ""}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Persist</Label>
              <Input className='checkbox-input'
                     type="checkbox"
                     value={this.props.camera !== null ? store.cameras[this.props.camera].persist : false}
                     onChange={(event) => this.onChangePersist(event)}/>{' '}
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CaptureControl.contextType = AppContext
