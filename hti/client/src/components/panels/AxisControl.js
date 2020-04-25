import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Row, Col, Input, Label } from 'reactstrap'

export default class AxisControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
    }
  }

  setSpeeds () { }
  getSpeeds () { }
  track () { }
  stop () { }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel axis-control-panel'>
              <Row>
                <Col style={{ maxWidth: '280px' }}>
                  <Label style={{width: '80px'}} className='spitzmarke' for='ra-speed'>RA</Label>
                  <Input style={{width: '150px'}} id='ra-speed' className='number-input' placeholder="0.0" type="number" step="0.001" />
                  <br/>
                  <Label style={{width: '80px'}} className='spitzmarke' for='dec-speed'>Dec</Label>
                  <Input style={{width: '150px'}} id='dec-speed' className='number-input' placeholder="0.0" type="number" step="0.001" />
                </Col>
                <Col style={{ maxWidth: '160px' }}>
                  <StandardButton onClick={() => { this.setSpeeds() }}>SET</StandardButton>
                  <StandardButton onClick={() => { this.getSpeeds() }}>GET</StandardButton>
                </Col>
                <Col style={{ maxWidth: '160px' }}>
                  <StandardButton onClick={() => { this.track() }}>TRACK</StandardButton>
                  <StandardButton onClick={() => { this.stop() }}>STOP</StandardButton>
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
