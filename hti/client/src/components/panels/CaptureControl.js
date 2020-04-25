import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Row, Col, Input, Label } from 'reactstrap'

export default class CameraView extends Component {
  constructor (props) {
    super(props)
    this.state = {
    }
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='panel capture-control-panel'>
            <Row>
              <Col style={{ maxWidth: '280px' }}>
                <Label style={{width: '100px'}} className='spitzmarke' for="exposure">Exposure</Label>
                <Input style={{width: '130px'}} className='number-input' type="number" id="exposure" placeholder="0.2" value="0.2" />
                <br/>
                <Label style={{width: '100px'}} className='spitzmarke' for="gain">Gain</Label>
                <Input style={{width: '130px'}} className='number-input' type="number" id="gain" placeholder="100" value="100" />
              </Col>
              <Col style={{ maxWidth: '180px' }}>
                <StandardButton id="capture">Capture</StandardButton>
              </Col>
              <Col style={{ width: '400px' }}>
                <Label style={{width: '120px'}} className='spitzmarke' for="pathprefix">Path Prefix</Label>
                <Input style={{width: '200px'}} className='number-input' type="string" id="pathprefix" placeholder="Images" value="Ímages" />
              </Col>
              <Col style={{ maxWidth: '200px' }}>
                <StandardButton id="start-sequence">Sequence</StandardButton>
                <StandardButton id="stop-sequence">Stop</StandardButton>
              </Col>
            </Row>
          </div>
        )}
      </AppConsumer>
    )
  }
}

CameraView.contextType = AppContext
