import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

export default class CameraView extends Component {
  constructor (props) {
    super(props)

    // TODO restore /devices endpoint with pyindi client, support multiple cameras
    this.camera = null

    this.state = {
      exposure: 10,
      gain: 10000,
      frameType: 'lights'
    }
  }

  onChangeExposure (event) {
    this.setState({exposure: event.target.value})
  }

  onChangeGain (event) {
    this.setState({gain: event.target.value})
  }

  capture () {
    $backend.capture(this.camera, this.state.exposure, this.state.gain)
  }

  startSequence () {
    $backend.startSequence(this.camera, this.state.frameType, this.state.exposure, this.state.gain)
  }

  stopSequence () {
    $backend.stopSequence(this.camera)
  }

  render () {
    const store = this.context.store
    const panelStateClass = store.cameraSim ? 'panel-yellow' : (store.cameraConnected ? 'panel-green' : 'panel-red')
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel capture-control-panel ' + panelStateClass}>
            <div className='settings-column'>
              <div>
                <Label className='spaced-text' for="exposure">Exposure (s)</Label>
                <Input className='number-input'
                       type="number"
                       placeholder={this.state.exposure}
                       value={this.state.exposure}
                       onChange={(event) => this.onChangeExposure(event)} />
              </div>
              <div>
                <Label className='spaced-text' for="gain">Gain</Label>
                <Input className='number-input'
                       type="number"
                       placeholder={this.state.gain}
                       value={this.state.gain}
                       onChange={(event) => this.onChangeGain(event)} />
              </div>
            </div>
            <div className='button-column'>
              <StandardButton id="capture"
                      disabled={!store.cameraConnected || store.capturing || store.runningSequence}
                      onClick={this.capture.bind(this)}>Capture</StandardButton>
              { store.runningSequence ?
                <StandardButton id="stop-sequence"
                        disabled={!store.cameraConnected}
                        onClick={this.stopSequence.bind(this)}>Stop</StandardButton>
              :
                <StandardButton id="start-sequence"
                        disabled={!store.cameraConnected || store.capturing}
                        onClick={this.startSequence.bind(this)}>Sequence</StandardButton>
              }
            </div>
            <div className='button-column'>
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
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
