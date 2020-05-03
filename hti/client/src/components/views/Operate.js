import React, { Component } from 'react'

import CameraView from '../panels/CameraView'
import CaptureControl from '../panels/CaptureControl'
import AxisControl from '../panels/AxisControl'
import TrackingControl from '../panels/TrackingControl'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { Row, Col } from 'reactstrap'

export default class Operate extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='operate'>
            <Col>
              <Row>
                <CameraView />
                <TrackingControl />
              </Row>
              <Row>
                <CaptureControl />
              </Row>
              <Row>
                <AxisControl />
              </Row>
            </Col>
          </div>
        )}
      </AppConsumer>
    )
  }
}
Operate.contextType = AppContext
