import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';

export default class CameraView extends Component {
  constructor (props) {
    super(props)

    this.state = {
      exposure: 1,
      gain: 100,
      sequencing: false,
      imageType: 'lights'
    }
  }

  onChangeExposure (event) {
    this.setState({exposure: event.target.value})
  }

  onChangeGain (event) {
    this.setState({gain: event.target.value})
  }

  capture () {
    this.context.mutations.capture(this.state.exposure, this.state.gain)
  }

  startSequence () {
    this.setState({sequencing: true})
    this.context.mutations.startSequence(this.state.imageType, this.state.exposure, this.state.gain)
  }

  stopSequence () {
    this.context.mutations.stopSequence().then(() => {
      this.setState({sequencing: false})
    })
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='panel capture-control-panel'>
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
                      disabled={!store.initialized || this.state.sequencing}
                      onClick={this.capture.bind(this)}>Capture</StandardButton>
              { this.state.sequencing ?
                <StandardButton id="stop-sequence"
                        disabled={!store.initialized}
                        onClick={this.stopSequence.bind(this)}>Stop</StandardButton>
              :
                <StandardButton id="start-sequence"
                        disabled={!store.initialized}
                        onClick={this.startSequence.bind(this)}>Sequence</StandardButton>
              }
            </div>
            <div className='button-column'>
              <UncontrolledDropdown>
                <DropdownToggle caret>{this.state.imageType}</DropdownToggle>
                <DropdownMenu>
                  <DropdownItem onClick={() => {this.setState({imageType: 'lights'})}}>Lights</DropdownItem>
                  <DropdownItem onClick={() => {this.setState({imageType: 'darks'})}}>Darks</DropdownItem>
                  <DropdownItem onClick={() => {this.setState({imageType: 'flats'})}}>Flats</DropdownItem>
                  <DropdownItem onClick={() => {this.setState({imageType: 'other'})}}>Other</DropdownItem>
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
