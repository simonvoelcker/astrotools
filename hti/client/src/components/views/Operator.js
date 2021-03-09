import React, { Component } from 'react'

import CameraView from '../panels/CameraView'
import LogView from '../panels/LogView'
import CaptureControl from '../panels/CaptureControl'
import AxisControl from '../panels/AxisControl'
import TrackingControl from '../panels/TrackingControl'
import PECControl from '../panels/PECControl'
import FocusControl from '../panels/FocusControl'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class Operator extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='operator'>
            <div className='left-column'>
              <CameraView />
              <LogView />
            </div>
            <div className='right-column'>
              <TrackingControl />
              <CaptureControl />
              <FocusControl />
              <AxisControl />
              <PECControl />
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}
Operator.contextType = AppContext
