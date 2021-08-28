import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import $backend from '../../backend'

export default class GuidingControl extends Component {

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel'}>
            { store.guiding ?
              <StandardButton onClick={() => $backend.stopGuiding(this.props.camera)}>Stop guiding</StandardButton>
            :
              <StandardButton onClick={() => $backend.startGuiding(this.props.camera)}>Start guiding</StandardButton>
            }
          </div>
        )}
      </AppConsumer>
    )
  }
}

GuidingControl.contextType = AppContext
