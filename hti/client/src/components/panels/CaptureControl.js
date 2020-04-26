import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Row, Col, Input, Label } from 'reactstrap'

export default class CameraView extends Component {
  constructor (props) {
    super(props)

    this.state = {
      exposure: 0.2,
      gain: 100,
      pathPrefix: '',
      capturing: false
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
            <Row>
              <Col style={{ maxWidth: '280px' }}>
                <Label style={{width: '100px'}} className='spitzmarke' for="exposure">Exposure</Label>
                <Input style={{width: '130px'}}
                        className='number-input'
                        type="number"
                        placeholder={this.state.exposure}
                        value={this.state.exposure}
                        onChange={(event) => this.onChangeExposure(event)} />
                <br/>
                <Label style={{width: '100px'}} className='spitzmarke' for="gain">Gain</Label>
                <Input style={{width: '130px'}}
                        className='number-input'
                        type="number"
                        placeholder={this.state.gain}
                        value={this.state.gain}
                        onChange={(event) => this.onChangeGain(event)} />
              </Col>
              <Col style={{ maxWidth: '180px' }}>
                <StandardButton id="capture"
                        disabled={!store.initialized || this.state.capturing}
                        onClick={this.capture.bind(this)}>Capture</StandardButton>
              </Col>
              <Col style={{ width: '400px' }}>
                <Label style={{width: '120px'}} className='spitzmarke' for="pathprefix">Path Prefix</Label>
                <Input style={{width: '200px'}}
                        className='number-input'
                        type="string"
                        id="pathprefix"
                        placeholder={this.state.pathPrefix}
                        value={this.state.pathPrefix}
                        onChange={(event) => this.onChangePathPrefix(event)} />
              </Col>
              <Col style={{ maxWidth: '200px' }}>
                <StandardButton id="start-sequence"
                        disabled={!store.initialized || this.state.capturing}
                        onClick={this.startSequence.bind(this)}>Sequence</StandardButton>
                <StandardButton id="stop-sequence"
                        disabled={!store.initialized || !this.state.capturing}
                        onClick={this.stopSequence.bind(this)}>Stop</StandardButton>
              </Col>
            </Row>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
