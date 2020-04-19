import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { formatTemperature } from '../../Utils.js'
import SpinnerButton from './SpinnerButton'

export default class DoorControl extends Component {
  render () {
    let temperatures = this.context.store.temperatures
    const isResuming = (this.context.store.printingNow && this.context.store.isPaused && this.context.store.isHeatingUp)
    const actualBed = formatTemperature(temperatures.arBed)
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div>
            <div>Environment Control { store.doorStatus.doorOpen ? <span style={{ color: 'red' }}> A door is open</span> : '' }</div>
            <div data-cy='DoorControl' id='door-control' className='button-holder button-pair' style={{ flexDirection: 'row' }}>
              <SpinnerButton
                disabled={store.doorStatus.doorLocked || store.pendingRequest === 'lockDoor' || store.doorStatus.doorOpen || isResuming}
                onClick={() => mutations.lockDoor()}
                request='lockDoor'>
                Lock door
              </SpinnerButton>
              <SpinnerButton
                disabled={!store.doorStatus.doorLocked || store.pendingRequest === 'unlockDoor' || store.doorStatus.doorOpen || isResuming}
                onClick={() => {
                  if (actualBed >= 80) {
                    mutations.toggleModal('showUnlockDoorModal')
                  } else {
                    mutations.unlockDoor()
                  }
                }}
                request='unlockDoor'>
                Unlock door
              </SpinnerButton>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

DoorControl.contextType = AppContext
