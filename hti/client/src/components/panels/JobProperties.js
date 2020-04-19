import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { formatPrintTimes, getJobTimeEstimate, createPrintEndDayString, createPrintEndDateString } from '../../Utils'
import { getGcodeFile } from '../../Utils'

export default class JobProperties extends Component {
  constructor (props) {
    super(props)

    this.state = {
      timeLeftEstimated: { hours: '00', minutes: '00', seconds: '00' },
      dayStopEstimated: 'Unknown',
      timeStopEstimated: '' // estimated timestamp for finished print
    }
  }

  componentDidMount () {
    this.updateTimes()
    this.timerID = setInterval(() => this.updateTimes(), 1000)
  }

  componentWillUnmount () {
    clearInterval(this.timerID)
  }

  extractExtruderInfo = (extruder) => {
    let extruderInfo = (extruder && extruder.active
      ? extruder.position.concat(
        ' ',
        extruder.variant,
        ' ',
        extruder.material.type,
        ' ',
        extruder.material_temperature,
        '°C')
      : ''
    )
    return extruderInfo
  }

  updateTimes () {
    let jobTimeEstimate = getJobTimeEstimate(this.context.store.jobQueue[0], this.context.store.printingNow)
    let secondsRemaining = jobTimeEstimate

    if (jobTimeEstimate !== null &&
        this.context.store.printingNow &&
        this.context.store.runningCommand === null &&
        this.context.store.elapsedPrintTime !== null) {
      let progressedTime =  Math.round(jobTimeEstimate * this.context.store.printProgress)
      secondsRemaining = Math.max(0, jobTimeEstimate - progressedTime)
    }

    this.setState({ timeLeftEstimated: formatPrintTimes(secondsRemaining) })
    this.setState({ dayStopEstimated: createPrintEndDayString(secondsRemaining) })
    this.setState({ timeStopEstimated: createPrintEndDateString(secondsRemaining) })
  }

  shouldComponentUpdate (nextProps, prevState) {
    return true
  }

  render () {
    const { timeLeftEstimated, dayStopEstimated, timeStopEstimated } = this.state

    const job = this.context.store.jobQueue[0]
    let compatibilityMessage = ''
    if (job) {
      if (getGcodeFile(job)) {
        if (!job.compatibility.slicerVersion || job.compatibility.slicerVersion === 'Unknown') {
          compatibilityMessage = 'Job does not have Blade version information'
        } else if (!job.compatibility.slicerCompatible) {
          compatibilityMessage = 'Job was created with an incompatible version of Blade'
        }
      }
    }

    return (
      <AppConsumer>

        {({ store, mutations }) => (
          <div style={{ display: 'flex', flexDirection: 'row' }}>
            <div data-cy='JobProperties' style={{ width: '66%', justifyContent: 'space-between', display: 'flex', flexDirection: 'column' }}>
              <div>
                Current Job <span style={{ color: 'red', fontSize: '12px' }}>{compatibilityMessage}</span>
                <h1 style={{ textAlign: 'left' }}>{job ? job.name : '(No job in queue)'}</h1>
                <p className='spitzmarke' style={{ margin: 0 }}>
                  {store.extruderSettingsArray
                    ? this.extractExtruderInfo(store.extruderSettingsArray[0])
                    : ''
                  }
                </p>
                <p className='spitzmarke'>
                  {store.extruderSettingsArray
                    ? this.extractExtruderInfo(store.extruderSettingsArray[1])
                    : ''
                  }
                </p>
                <br />
              </div>
              <div data-cy='TimeLeftEstimated'>
                {store.printingNow && !store.isHeatingUp && store.runningCommand === null ? 'Estimated time left' : 'Estimated time'}
                <h1 className='timeString'>
                  {timeLeftEstimated.hours}
                  <span style={{ marginRight: '8px' }}>h</span>
                  {timeLeftEstimated.minutes}
                  <span style={{ marginRight: '8px' }}>m</span>
                </h1>
              </div>
            </div>
            {store.printingNow && !store.isHeatingUp && store.runningCommand === null &&
              <div data-cy='TUNA' style={{ width: '33%' }} >
                Job complete on
                <h1>{dayStopEstimated}<br />{timeStopEstimated}</h1>
              </div>
            }
          </div>
        )}

      </AppConsumer>
    )
  }
}

JobProperties.contextType = AppContext