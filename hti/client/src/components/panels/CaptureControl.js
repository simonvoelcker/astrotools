import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

export default class CameraView extends Component {

  updateCameraSettings () {
    $backend.updateCameraSettings(
      this.props.camera,
      this.context.store.cameras[this.props.camera].exposure,
      this.context.store.cameras[this.props.camera].gain,
      this.context.store.cameras[this.props.camera].persist,
      this.context.store.cameras[this.props.camera].frameType,
    )
  }

  onChangeExposure (event) {
    this.context.store.cameras[this.props.camera].exposure = event.target.value
    this.updateCameraSettings()
  }

  onChangeGain (event) {
    this.context.store.cameras[this.props.camera].gain = event.target.value
    this.updateCameraSettings()
  }

  onChangePersist (event) {
    this.context.store.cameras[this.props.camera].persist = event.target.checked
    this.updateCameraSettings()
  }

  onFrameTypeChange (frameType) {
    this.context.store.cameras[this.props.camera].frameType = frameType
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
              <Label className='spaced-text'>Exposure (s)</Label>
              <Input className='number-input'
                     type="number"
                     placeholder="1"
                     disabled={this.props.camera === null}
                     value={this.props.camera !== null ? store.cameras[this.props.camera].exposure : 1}
                     onChange={(event) => this.onChangeExposure(event)} />
            </div>
            <div className='settings-row'>
              <Label className='spaced-text'>Gain</Label>
              <Input className='number-input'
                     type="number"
                     placeholder="1"
                     disabled={this.props.camera === null}
                     value={this.props.camera !== null ? store.cameras[this.props.camera].gain : 1}
                     onChange={(event) => this.onChangeGain(event)} />
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Frame type</Label>
              <UncontrolledDropdown disabled={this.props.camera === null}>
                <DropdownToggle caret>{this.props.camera !== null ? store.cameras[this.props.camera].frameType : '-'}</DropdownToggle>
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

CameraView.contextType = AppContext
