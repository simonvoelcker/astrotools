import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import SpinnerButton from './SpinnerButton'

export default class AbortPauseWidget extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='button-holder button-pair' style={{ flexDirection: 'row' }}>
            { !!store.runningCommand
              ? <SpinnerButton
                datacy='Abort'
                onClick={() => mutations.stopCommand()}
                disabled={!!store.pendingRequest}
                request='stopJob'>
                Abort
              </SpinnerButton>
              : <SpinnerButton
                datacy='AbortJob'
                onClick={() => mutations.toggleModal('showAbortModal')}
                disabled={!!store.pendingRequest}
                request='stopJob'>
                Abort Job
              </SpinnerButton>
            }
            { store.isPaused
              ? <SpinnerButton
                onClick={() => { mutations.resume() }}
                datacy='ResumeJob'
                disabled={!!store.pendingRequest || !mutations.canStartOrResumeJob() || store.isHeatingUp || store.mode === 'demo'}
                request='resumeJob'>
                Resume Job
              </SpinnerButton>
              : <SpinnerButton
                onClick={() => { mutations.pause() }}
                datacy='PauseJob'
                disabled={!!store.pendingRequest || !!store.runningCommand || store.isHeatingUp || store.mode === 'demo'}
                request='pauseJob'>
                Pause Job
              </SpinnerButton>
            }
          </div>
        )}
      </AppConsumer>
    )
  }
}

AbortPauseWidget.contextType = AppContext
