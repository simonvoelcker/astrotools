import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input, Label } from 'reactstrap'

export default class CameraView extends Component {
  constructor (props) {
    super(props)

    this.state = {
      exposure: 1,
      gain: 100,
      pathPrefix: '',
      capturing: false,
    }
  }

  onChangeExposure (event) {
    this.setState({exposure: event.target.value})
  }

  onChangeGain (event) {
    this.setState({gain: event.target.value})
  }

  onChangePathPrefix (event) {
    this.setState({pathPrefix: event.target.value})
  }

  capture () {
    this.setState({capturing: true})
    this.context.mutations.capture(this.state.exposure, this.state.gain).then(() => {
      this.setState({capturing: false})
    })
  }

  startSequence () {
    this.setState({capturing: true})
    this.context.mutations.startSequence(this.state.pathPrefix, this.state.exposure, this.state.gain)
  }

  stopSequence () {
    this.context.mutations.stopSequence().then(() => {
      this.setState({capturing: false})
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
                      disabled={!store.initialized || this.state.capturing}
                      onClick={this.capture.bind(this)}>Capture</StandardButton>
            </div>
            <div className='button-column'>
              <StandardButton id="start-sequence"
                      disabled={!store.initialized || this.state.capturing}
                      onClick={this.startSequence.bind(this)}>Sequence</StandardButton>
              <StandardButton id="stop-sequence"
                      disabled={!store.initialized || !this.state.capturing}
                      onClick={this.stopSequence.bind(this)}>Stop</StandardButton>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
