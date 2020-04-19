import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'

export default class VersionInfo extends Component {
  getHmiVersion = (store) => {
    let versionInfo = store.versionInfo
    if (versionInfo != null && versionInfo.hmiVersion !== undefined) {
      let line = 'V' + versionInfo.hmiVersion
      if (versionInfo.hmiBuild !== null) {
        line += '-' + versionInfo.hmiBuild
      }
      return line
    }
    return 'Loading ...'
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <p className='version-info'>
            {this.getHmiVersion(store)}
          </p>
        )}
      </AppConsumer>
    )
  }
}

VersionInfo.contextType = AppContext
