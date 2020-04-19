import React, { Component } from 'react'

import CallToAction from '../panels/CallToAction'
import JobProperties from '../panels/JobProperties'
import UploadJobWidget from '../panels/UploadJobWidget'
import JobList from '../panels/JobList'
import PrintingStatusIndicator from '../panels/PrintingStatusIndicator'
import { AppConsumer } from '../../context/AppContext'

export default class SceneInfos extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className='scene scene-infos'>

            <div className='panel' style={{ width: '885px', minHeight: '256px' }} >
              <JobProperties />
            </div>

            <div style={{ display: 'flex', flexDirection: 'row', marginTop: '15px' }}>
              <CallToAction />
              <PrintingStatusIndicator />
              <UploadJobWidget title="USB UPLOAD" size="3"/>
            </div>

            <JobList scene='SceneInfos' />
          </div>
        )}
      </AppConsumer>
    )
  }
}
