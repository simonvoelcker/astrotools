import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Row, Col, Input, Label } from 'reactstrap'

export default class TrackingControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
    }
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel tracking-control-panel'>
              <Row>
                <Col style={{ maxWidth: '350px' }}>
                  <Label style={{width: '80px'}} className='spitzmarke' for='target-input'>Target</Label>
                  <Input style={{width: '230px'}} id='target-input' className='number-input' placeholder="Object name or coordinates" type="text" />
                </Col>
                <Col style={{ maxWidth: '160px' }}>
                  <StandardButton onClick={() => { }}>SET</StandardButton>
                </Col>
                <Col style={{ maxWidth: '280px' }}>
                  <StandardButton onClick={() => { }}>TRACK TARGET</StandardButton>
                  <StandardButton onClick={() => { }}>TRACK IMAGE</StandardButton>
                </Col>
              </Row>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

TrackingControl.contextType = AppContext
