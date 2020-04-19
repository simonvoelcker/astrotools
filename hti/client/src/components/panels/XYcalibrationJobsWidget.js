import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import SpinnerButton from '../panels/SpinnerButton'

export default class XYcalibrationJobsWidget extends Component {
  getCalibrationJobAddButton = (store, mutations, jobFile, jobName, buttonText) => {
    return <SpinnerButton
              className='btn'
              disabled={store.mode === 'demo'}
              onClick={() => { mutations.loadCalibrationJob(jobFile, jobName) }}
              request={jobName} >
              {buttonText}
            </SpinnerButton>
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div data-cy='CalibJobs'>
            <div style={{ width: '100%', textAlign: 'center' }}>XY Extruder Offset Calibration</div>
            {this.getCalibrationJobAddButton(store, mutations, '_xyCalib05', 'XY Calibration (0.5mm)', 'Load Job, Accuracy 0.5')}
            {this.getCalibrationJobAddButton(store, mutations, '_xyCalib01', 'XY Calibration (0.1mm)', 'Load Job, Accuracy 0.1')}
          </div>
        )}
      </AppConsumer>
    )
  }
}

XYcalibrationJobsWidget.contextType = AppContext
