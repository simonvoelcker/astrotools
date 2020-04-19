import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import AbortPauseWidget from '../panels/AbortPauseWidget'
import SpinnerButton from './SpinnerButton'

export default class CallToAction extends Component {
  getCurrentButton = (store, mutations) => {
    let disabled = store.pendingRequest !== null

    if (this.context.store.jobQueue[0] && this.context.store.jobQueue[0].hmiUpdateFile) {
      return <div>
        <SpinnerButton datacy='StartUpdate' onClick={mutations.startUpdate} disabled={disabled} request='startUpdate'>Start HMI Update</SpinnerButton>
      </div>
    }

    if (!store.printingNow) {
      disabled = disabled || !store.jobQueue[0] || !this.context.mutations.canStartOrResumeJob()
      return <div>
        <SpinnerButton datacy='StartJob' onClick={mutations.handleJobStartRequest} disabled={disabled} request='startJob'>Start Job</SpinnerButton>
      </div>
    }

    return <AbortPauseWidget />
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div data-cy='CallToAction' style={{ width: '462px' }}>
            {this.getCurrentButton(store, mutations)}
          </div>
        )}
      </AppConsumer>
    )
  }
}

CallToAction.contextType = AppContext // This part is important to access context values
