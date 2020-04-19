import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import SpinnerButton from './SpinnerButton'

export default class AxisControl extends Component {

  canHome () {
    let store = this.context.store
    return store.hmiCommands.homeAxes && !store.machineHomed && !store.doorStatus.doorOpen
  }

  canPark () {
    let store = this.context.store
    return (
      store.hmiCommands.parkingPosition &&
      store.machineHomed &&
      !store.doorStatus.doorOpen &&
      !store.printingNow &&
      !store.isPaused &&
      store.mode !== 'demo'
    )
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='button-panel'>
            <div>Axis Control</div>
            <SpinnerButton
              datacy='HomeAxes'
              disabled={!this.canHome()}
              onClick={() => mutations.toggleModal('showConfirmHomeModal')}
              request='homePrinter'>
              Home Axes
            </SpinnerButton>
            <SpinnerButton
              datacy='ParkingPosition'
              disabled={!this.canPark()}
              onClick={() => { mutations.runCommand(store.hmiCommands.parkingPosition) }}
              request={store.hmiCommands.parkingPosition.id}>
              Parking Position
            </SpinnerButton>
          </div>
        )}
      </AppConsumer>
    )
  }
}

AxisControl.contextType = AppContext
