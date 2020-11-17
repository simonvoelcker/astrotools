import React, { Component } from 'react'

import ThreeDView from '../panels/ThreeDView'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class Viewer extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='viewer'>
            <ThreeDView />
          </div>
        )}
      </AppConsumer>
    )
  }
}
Viewer.contextType = AppContext
