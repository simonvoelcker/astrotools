import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

export default class CameraView extends Component {
  constructor (props) {
    super(props)

    this.state = {
      camera: null,
    }
  }

  updateCameraSettings () {
    $backend.updateCameraSettings(
      this.state.camera,
      this.context.store.cameras[this.state.camera].exposure,
      this.context.store.cameras[this.state.camera].gain,
      this.context.store.cameras[this.state.camera].persist,
      this.context.store.cameras[this.state.camera].frameType,
    )
  }

  onChangeExposure (event) {
    this.context.store.cameras[this.state.camera].exposure = event.target.value
    this.updateCameraSettings()
  }

  onChangeGain (event) {
    this.context.store.cameras[this.state.camera].gain = event.target.value
    this.updateCameraSettings()
  }

  onChangePersist (event) {
    this.context.store.cameras[this.state.camera].persist = event.target.checked
    this.updateCameraSettings()
  }

  onFrameTypeChange (frameType) {
    this.context.store.cameras[this.state.camera].frameType = frameType
    this.updateCameraSettings()
  }

  capture () {
    $backend.capture(this.state.camera)
  }

  startSequence () {
    $backend.startSequence(this.state.camera)
  }

  stopSequence () {
    $backend.stopSequence(this.state.camera)
  }

  render () {
    const store = this.context.store
    const panelStateClass = (this.state.camera !== null ? 'panel-green' : 'panel-red')
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel capture-control-panel ' + panelStateClass}>

            <div className='settings-row'>
              <Label className='spaced-text'>Camera</Label>
              <UncontrolledDropdown>
                <DropdownToggle caret>{this.state.camera || 'None'}</DropdownToggle>
                <DropdownMenu>
                  <DropdownItem onClick={() => {this.setState({camera: null})}}>None</DropdownItem>
                  {Object.keys(store.cameras).map((cameraName) => (
                    <DropdownItem onClick={() => {this.setState({camera: cameraName})}}>{cameraName}</DropdownItem>
                  ))}
                </DropdownMenu>
              </UncontrolledDropdown>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Exposure (s)</Label>
              <Input className='number-input'
                     type="number"
                     placeholder="1"
                     disabled={this.state.camera === null}
                     value={this.state.camera !== null ? store.cameras[this.state.camera].exposure : 1}
                     onChange={(event) => this.onChangeExposure(event)} />
            </div>
            <div className='settings-row'>
              <Label className='spaced-text'>Gain</Label>
              <Input className='number-input'
                     type="number"
                     placeholder="1"
                     disabled={this.state.camera === null}
                     value={this.state.camera !== null ? store.cameras[this.state.camera].gain : 1}
                     onChange={(event) => this.onChangeGain(event)} />
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Frame type</Label>
              <UncontrolledDropdown disabled={this.state.camera === null}>
                <DropdownToggle caret>{this.state.camera !== null ? store.cameras[this.state.camera].frameType : '-'}</DropdownToggle>
                <DropdownMenu>
                  <DropdownItem onClick={() => {this.onFrameTypeChange('lights')}}>Lights</DropdownItem>
                  <DropdownItem onClick={() => {this.onFrameTypeChange('darks')}}>Darks</DropdownItem>
                  <DropdownItem onClick={() => {this.onFrameTypeChange('flats')}}>Flats</DropdownItem>
                </DropdownMenu>
              </UncontrolledDropdown>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Single capture</Label>
              <StandardButton id="capture"
                      disabled={
                        this.state.camera === null ||
                        store.cameras[this.state.camera].capturing ||
                        store.cameras[this.state.camera].runningSequence
                      }
                      onClick={this.capture.bind(this)}>Capture</StandardButton>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Sequence</Label>
              { this.state.camera !== null && store.cameras[this.state.camera].runningSequence ?
                <StandardButton id="stop-sequence"
                        disabled={this.state.camera === null}
                        onClick={this.stopSequence.bind(this)}>Stop</StandardButton>
              :
                <StandardButton id="start-sequence"
                        disabled={this.state.camera === null || store.cameras[this.state.camera].capturing}
                        onClick={this.startSequence.bind(this)}>Start</StandardButton>
              }
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Persist</Label>
              <Input className='checkbox-input'
                     type="checkbox"
                     value={this.state.camera !== null ? store.cameras[this.state.camera].persist : false}
                     onChange={(event) => this.onChangePersist(event)}/>{' '}
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
