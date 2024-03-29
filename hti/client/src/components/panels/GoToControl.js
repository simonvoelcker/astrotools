import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Row, Col, Input } from 'reactstrap'
import $backend from '../../backend'


export default class GoToControl extends Component {
  constructor (props) {
    super(props)
    this.interval = null
    this.state = {
      targetInput: '',
      targetInputStatus: '',
      target: null,
      time: Date.now(),
    }
  }

  componentDidMount() {
    this.interval = setInterval(() => this.setState({ time: Date.now() }), 1000)
  }

  componentWillUnmount() {
    clearInterval(this.interval)
  }

  onChangeTargetInput (event) {
    this.setState({targetInput: event.target.value})
  }

  onSetTarget () {
    let query = this.state.targetInput
    this.setState({targetInputStatus: ''})
    $backend.queryTarget(query).then(response => {
      this.setState({target: response.data})
    }).catch(error => {
      this.setState({targetInputStatus: 'Not found'})
    })
  }

  formatTarget () {
    if (this.state.target !== null) {
      return this.state.target.ra.toFixed(2) + ', ' + this.state.target.dec.toFixed(2)
    }
    return 'Not set'
  }

  formatCurrentCoordinates() {
    let calib = this.context.store.lastKnownPosition
    if (calib !== null && calib.timestamp !== null && calib.position !== null) {
      const timestamp = Math.floor(this.state.time / 1000)
      const passedTime = timestamp - calib.timestamp
      return calib.position.ra.toFixed(2) + ', ' + calib.position.dec.toFixed(2) + ' (' + passedTime + 's ago)'
    }
    return 'Unknown'
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel tracking-control-panel'>
              <span className='spaced-text panel-title'>Target Control</span>
              <Col>
                <Row className='row target-selection-row'>
                  <Input
                    id='target-input'
                    className='number-input'
                    placeholder="Target name or coordinates"
                    type="text"
                    value={this.state.targetInput}
                    onChange={this.onChangeTargetInput.bind(this)} />
                  <span className="spaced-text">{this.state.targetInputStatus}</span>
                  <button className='btn' onClick={this.onSetTarget.bind(this)}>SET</button>
                </Row>

                <Row className='row current-target-row'>
                  <span className="spaced-text">Target coordinates: {this.formatTarget()}</span>
                  <button className='btn'
                    disabled={this.state.target === null || store.tracking || store.steering || store.imagePosition === null}
                    onClick={$backend.goToTarget}>GO TO</button>
                </Row>

                <Row className='row current-position-row'>
                  <span className="spaced-text">Current coordinates: {this.formatCurrentCoordinates()}</span>
                  { store.calibrating ?
                    <button className='btn' onClick={$backend.stopCalibration}>ABORT</button>
                  :
                    <button className='btn' disabled={store.capturingCamera === null || store.framePathByDeviceName[store.capturingCamera] === null}
                      onClick={() => $backend.calibrateFrame(store.framePathByDeviceName[store.capturingCamera], 30)}>UPDATE</button>
                  }
                </Row>

              </Col>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

GoToControl.contextType = AppContext
