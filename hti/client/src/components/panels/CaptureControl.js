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
      exposure: 1,
      gain: 20000,
      persist: false,
      frameType: 'lights'
    }
  }

  onChangeExposure (event) {
    this.setState({exposure: event.target.value})
  }

  onChangeGain (event) {
    this.setState({gain: event.target.value})
  }

  onChangePersist (event) {
    this.setState({persist: event.target.checked})
  }

  capture () {
    $backend.capture(this.state.exposure, this.state.gain, this.state.persist)
  }

  startSequence () {
    $backend.startSequence(this.state.frameType, this.state.exposure, this.state.gain, this.state.persist)
  }

  stopSequence () {
    $backend.stopSequence()
  }

  render () {
    const store = this.context.store
    const panelStateClass = store.cameraSim ? 'panel-yellow' : (store.cameraConnected ? 'panel-green' : 'panel-red')
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
                  {store.connectedCameras.map((cameraName) => (
                    <DropdownItem onClick={() => {this.setState({camera: cameraName})}}>{cameraName}</DropdownItem>
                  ))}
                </DropdownMenu>
              </UncontrolledDropdown>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Exposure (s)</Label>
              <Input className='number-input'
                     type="number"
                     placeholder={this.state.exposure}
                     value={this.state.exposure}
                     onChange={(event) => this.onChangeExposure(event)} />
            </div>
            <div className='settings-row'>
              <Label className='spaced-text'>Gain</Label>
              <Input className='number-input'
                     type="number"
                     placeholder={this.state.gain}
                     value={this.state.gain}
                     onChange={(event) => this.onChangeGain(event)} />
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Frame type</Label>
              <UncontrolledDropdown>
                <DropdownToggle caret>{this.state.frameType}</DropdownToggle>
                <DropdownMenu>
                  <DropdownItem onClick={() => {this.setState({frameType: 'preview'})}}>Preview</DropdownItem>
                  <DropdownItem onClick={() => {this.setState({frameType: 'lights'})}}>Lights</DropdownItem>
                  <DropdownItem onClick={() => {this.setState({frameType: 'darks'})}}>Darks</DropdownItem>
                  <DropdownItem onClick={() => {this.setState({frameType: 'flats'})}}>Flats</DropdownItem>
                  <DropdownItem onClick={() => {this.setState({frameType: 'other'})}}>Other</DropdownItem>
                </DropdownMenu>
              </UncontrolledDropdown>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Single capture</Label>
              <StandardButton id="capture"
                      disabled={this.state.camera === null || store.capturing || store.runningSequence}
                      onClick={this.capture.bind(this)}>Capture</StandardButton>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Sequence</Label>
              { store.runningSequence ?
                <StandardButton id="stop-sequence"
                        disabled={this.state.camera === null}
                        onClick={this.stopSequence.bind(this)}>Stop</StandardButton>
              :
                <StandardButton id="start-sequence"
                        disabled={this.state.camera === null || store.capturing}
                        onClick={this.startSequence.bind(this)}>Start</StandardButton>
              }
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Persist</Label>
              <Input className='checkbox-input'
                     type="checkbox"
                     value={this.state.persist}
                     onChange={(event) => this.onChangePersist(event)}/>{' '}
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
