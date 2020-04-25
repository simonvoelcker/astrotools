import React, { Component } from 'react'

import CameraView from '../panels/CameraView'
import CaptureControl from '../panels/CaptureControl'
import AxisControl from '../panels/AxisControl'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class Operate extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='operate'>
            <CameraView />
            <CaptureControl />
            <AxisControl />
          </div>
        )}
      </AppConsumer>
    )
  }
}
Operate.contextType = AppContext
