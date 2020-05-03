import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Row, Col, Input, Label } from 'reactstrap'

export default class AxisControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
      raSpeed: 0.0,
      decSpeed: 0.0
    }
  }

  getActualSpeeds () {
    this.context.mutations.getSpeeds().then(response => {
      this.setState({
        raSpeed: response.data.ra,
        decSpeed: response.data.dec
      })
    })
  }

  setSpeeds () {
    this.context.mutations.setSpeeds(this.state.raSpeed, this.state.decSpeed).then(() => {
      this.getActualSpeeds()
    })
  }

  rest () {
    this.context.mutations.setRest().then(() => {
      this.getActualSpeeds()
    })
  }

  stop () {
    this.context.mutations.setSpeeds(0.0, 0.0).then(() => {
      this.getActualSpeeds()
    })
  }

  onChangeRaSpeed (event) {
    this.setState({raSpeed: event.target.value})
  }

  onChangeDecSpeed (event) {
    this.setState({decSpeed: event.target.value})
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel axis-control-panel'>
              <Row>
                <Col style={{ maxWidth: '280px' }}>
                  <Label style={{width: '80px'}} className='spitzmarke' for='ra-speed'>RA</Label>
                  <Input style={{width: '150px'}}
                    id='ra-speed'
                    className='number-input'
                    type="number"
                    step="0.001"
                    value={this.state.raSpeed}
                    onChange={this.onChangeRaSpeed.bind(this)} />
                  <br/>
                  <Label style={{width: '80px'}} className='spitzmarke' for='dec-speed'>Dec</Label>
                  <Input style={{width: '150px'}}
                    id='dec-speed'
                    className='number-input'
                    placeholder="0.0"
                    type="number"
                    step="0.001"
                    value={this.state.decSpeed}
                    onChange={this.onChangeDecSpeed.bind(this)} />
                </Col>
                <Col style={{ maxWidth: '160px' }}>
                  <StandardButton onClick={this.setSpeeds.bind(this)}>SET</StandardButton>
                </Col>
                <Col style={{ maxWidth: '160px' }}>
                  <StandardButton onClick={this.rest.bind(this)}>REST</StandardButton>
                  <StandardButton onClick={this.stop.bind(this)}>STOP</StandardButton>
                </Col>
              </Row>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

AxisControl.contextType = AppContext
