import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Row, Col, Input, Label } from 'reactstrap'

export default class CameraView extends Component {
  constructor (props) {
    super(props)

    this.state = {
      exposure: 0.2,
      gain: 100
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
  }

  stopSequence () {
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
                <StandardButton id="capture" onClick={this.capture.bind(this)}>Capture</StandardButton>
              </Col>
              <Col style={{ width: '400px' }}>
                <Label style={{width: '120px'}} className='spitzmarke' for="pathprefix">Path Prefix</Label>
                <Input style={{width: '200px'}}
                        className='number-input'
                        type="string"
                        id="pathprefix"
                        placeholder="Images"
                        value="Ímages"
                        onChange={() => {}} />
              </Col>
              <Col style={{ maxWidth: '200px' }}>
                <StandardButton id="start-sequence" onClick={this.startSequence}>Sequence</StandardButton>
                <StandardButton id="stop-sequence" onClick={this.stopSequence}>Stop</StandardButton>
              </Col>
            </Row>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
