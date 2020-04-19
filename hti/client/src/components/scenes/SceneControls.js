import React, { Component } from 'react'
import DoorControl from '../panels/DoorControl'
import BedControls from '../panels/BedControls'
import AxisControl from '../panels/AxisControl'
import ExtruderControl from '../panels/ExtruderControl'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export default class SceneControls extends Component {
  controlsEnabled (store) {
    if (store.printingNow && !store.isPaused && !store.standbyWaitingUserAction) {
      return false
    }
    if (store.pendingRequest !== null) {
      return false
    }
    return true
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div className='scene scene-controls' data-cy='ControlsPage'>
            <div>
              <div style={{ display: 'flex', flexDirection: 'row' }}>
                <div className={this.controlsEnabled(store) ? 'panel' : 'panel disabled-element'} style={{ width: '540px' }}>
                  <DoorControl />
                  <AxisControl />
                </div>
              </div>
              <div style={{ width: '300px', position: 'absolute', right: '15px', top: '60px' }}>
                <StandardButton
                  datacy={'MachineInfoButton'}
                  onClick={() => { mutations.showMachineInfo(null) }}
                >
                  Machine Info
                </StandardButton>
                <StandardButton
                  datacy={'Reset'}
                  onClick={mutations.resetPrinter}
                  disabled={!!store.pendingRequest}
                >
                  Reset Error
                </StandardButton>
                <StandardButton
                  datacy={'ShowOffSetModal'}
                  onClick={() => { mutations.toggleModal('showOffSetModal') }}
                >
                  Tool Correction
                </StandardButton>
              </div>
              <div className={this.controlsEnabled(store) ? '' : 'disabled-element'} style={{ display: 'flex', flexDirection: 'row' }}>
                <ExtruderControl tool='t0' />
                <ExtruderControl tool='t1' />
                <BedControls />
              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

SceneControls.contextType = AppContext
