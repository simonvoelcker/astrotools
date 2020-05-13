import React, { Component } from 'react'

import CameraView from '../panels/CameraView'
import CaptureControl from '../panels/CaptureControl'
import AxisControl from '../panels/AxisControl'
import TrackingControl from '../panels/TrackingControl'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { Col } from 'reactstrap'

export default class Operate extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='operate'>
            <Col>
              <CameraView />
            </Col>
            <Col>
              <TrackingControl />
              <CaptureControl />
              <AxisControl />
            </Col>
          </div>
        )}
      </AppConsumer>
    )
  }
}
Operate.contextType = AppContext
