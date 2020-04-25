import React, { Component } from 'react'

import ManualAxisControl from '../panels/ManualAxisControl'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class Operate extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='operate'>
            <ManualAxisControl />
          </div>
        )}
      </AppConsumer>
    )
  }
}
Operate.contextType = AppContext
