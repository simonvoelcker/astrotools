import React, { Component } from 'react'

import CameraView from '../panels/CameraView'
import CaptureControl from '../panels/CaptureControl'
import AxisControl from '../panels/AxisControl'
import TrackingControl from '../panels/TrackingControl'
import ImageControl from '../panels/ImageControl'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class Operator extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='operator'>
            <div>
              <CameraView />
              <ImageControl />
            </div>
            <div>
              <TrackingControl />
              <CaptureControl />
              <AxisControl />
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}
Operator.contextType = AppContext
